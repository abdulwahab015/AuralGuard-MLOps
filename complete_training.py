"""
Complete training script for AuralGuard.
This script does everything: data preparation, training, and saving the model.
Run this instead of running notebook cells manually.
"""

import tensorflow as tf
from keras import Sequential
from keras.layers import Dense, Conv2D, Flatten, Input
import librosa
import soundfile as sf
import tensorflow_io as tfio
import numpy as np
import os
import sys

# Add utils to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from mlflow_tracking import MLflowTracker

print("=" * 60)
print("AuralGuard - Complete Training Script")
print("=" * 60)
print()

# ============================================================================
# STEP 1: Data Preparation - Create Audio Chunks
# ============================================================================

def convert_audio_to_chunks(path, filename, output_dir):
    """Convert large audio files to 15-second chunks. Pads short files."""
    wav, sr = librosa.load(path, sr=None)
    chunk_size = 15  # 15 seconds chunks
    
    chunk_samples = sr * chunk_size
    os.makedirs(output_dir, exist_ok=True)

    # If file is shorter than 15 seconds, pad it with zeros
    if len(wav) < chunk_samples:
        # Pad with zeros to make it exactly 15 seconds
        padding = np.zeros(chunk_samples - len(wav))
        wav = np.concatenate([wav, padding])
        file = f"chunk_0_{filename}"
        sf.write(os.path.join(output_dir, file), wav, sr)
        return None
    
    # For longer files, create chunks
    for i, start_sample in enumerate(range(0, len(wav), chunk_samples)):
        chunk = wav[start_sample:start_sample + chunk_samples]
        if len(chunk) < chunk_samples:
            # Pad the last chunk if it's shorter
            padding = np.zeros(chunk_samples - len(chunk))
            chunk = np.concatenate([chunk, padding])
        file = f"chunk_{i}_{filename}"
        sf.write(os.path.join(output_dir, file), chunk, sr)
    return None


def prepare_audio_chunks():
    """Prepare audio chunks from original dataset."""
    print("Step 1: Preparing audio chunks...")
    
    real_path = os.path.join('Audio Dataset', 'KAGGLE', 'AUDIO', 'REAL')
    fake_path = os.path.join('Audio Dataset', 'KAGGLE', 'AUDIO', 'FAKE')
    
    # Check if directories exist
    if not os.path.exists(real_path):
        print(f"ERROR: Real audio path not found: {real_path}")
        print("Please ensure your audio dataset is in the correct location.")
        return False
    
    if not os.path.exists(fake_path):
        print(f"ERROR: Fake audio path not found: {fake_path}")
        print("Please ensure your audio dataset is in the correct location.")
        return False
    
    # Create chunks
    print("  Creating chunks from real audio files...")
    real_files = os.listdir(real_path)
    for file in real_files:
        if file.endswith(('.wav', '.mp3', '.flac')):
            convert_audio_to_chunks(
                os.path.join(real_path, file), 
                file, 
                'real_audio_chunks'
            )
    
    print("  Creating chunks from fake audio files...")
    fake_files = os.listdir(fake_path)
    for file in fake_files:
        if file.endswith(('.wav', '.mp3', '.flac')):
            convert_audio_to_chunks(
                os.path.join(fake_path, file), 
                file, 
                'fake_audio_chunks'
            )
    
    print("  ✅ Audio chunks created successfully!")
    return True


# ============================================================================
# STEP 2: Load and Preprocess Audio
# ============================================================================

def load_wav_16k_mono(filename):
    """Load audio file and convert to 16kHz mono."""
    wav = tf.io.read_file(filename)
    wav, sr = tf.audio.decode_wav(wav, desired_channels=1)
    wav = tf.squeeze(wav, axis=1)
    sr = tf.cast(sr, dtype=tf.int64)
    wav = tfio.audio.resample(wav, rate_in=sr, rate_out=16000)
    return wav


def file_to_mel_spectrogram_by_lib(filename, label):
    """Convert file to mel-spectrogram."""
    def numpy_func(filename_tensor):
        wav, samp_rate = librosa.load(
            filename_tensor.numpy().decode('utf-8'), 
            sr=16000, 
            mono=True
        )
        # Ensure audio is exactly 15 seconds (240000 samples at 16kHz)
        target_length = 16000 * 15
        if len(wav) > target_length:
            wav = wav[:target_length]
        elif len(wav) < target_length:
            padding = np.zeros(target_length - len(wav))
            wav = np.concatenate([wav, padding])
        
        mel_spectrogram_numpy = librosa.feature.melspectrogram(
            y=wav, sr=samp_rate, n_mels=128, fmax=8000
        )
        mel_spectrogram_tf = tf.convert_to_tensor(
            mel_spectrogram_numpy, 
            dtype=tf.float32
        )
        return mel_spectrogram_tf

    mel_spectrogram = tf.py_function(
        numpy_func, 
        inp=[filename], 
        Tout=tf.float32
    )
    # Set explicit shape to avoid unknown rank issues
    mel_spectrogram.set_shape([128, 469])
    mel_spectrogram = tf.expand_dims(mel_spectrogram, axis=2)
    return mel_spectrogram, label


# ============================================================================
# STEP 3: Prepare Dataset
# ============================================================================

def prepare_dataset(real_chunks_path='real_audio_chunks', 
                   fake_chunks_path='fake_audio_chunks'):
    """Prepare TensorFlow dataset from audio chunks."""
    print("Step 2: Preparing dataset...")
    
    # Check if chunks exist
    if not os.path.exists(real_chunks_path):
        print(f"ERROR: {real_chunks_path} not found!")
        return None
    
    if not os.path.exists(fake_chunks_path):
        print(f"ERROR: {fake_chunks_path} not found!")
        return None
    
    # Create datasets
    real_chunks_examples = tf.data.Dataset.list_files(
        os.path.join(real_chunks_path, '*.wav')
    )
    fake_chunks_examples = tf.data.Dataset.list_files(
        os.path.join(fake_chunks_path, '*.wav')
    )
    
    # Get dataset sizes
    real_count = len(list(real_chunks_examples))
    fake_count = len(list(fake_chunks_examples))
    
    print(f"  Found {real_count} real audio chunks")
    print(f"  Found {fake_count} fake audio chunks")
    
    if real_count == 0 or fake_count == 0:
        print("ERROR: No audio chunks found!")
        return None
    
    # Create labels
    real_labels = tf.data.Dataset.from_tensor_slices(tf.ones(real_count))
    fake_labels = tf.data.Dataset.from_tensor_slices(tf.zeros(fake_count))
    
    # Zip with labels
    real_data = tf.data.Dataset.zip((real_chunks_examples, real_labels))
    fake_data = tf.data.Dataset.zip((fake_chunks_examples, fake_labels))
    
    # Concatenate
    data = real_data.concatenate(fake_data)
    
    # Map to mel-spectrograms
    print("  Converting to mel-spectrograms (this may take a while)...")
    data = data.map(file_to_mel_spectrogram_by_lib)
    data = data.cache()
    
    # Adjust batch size for small datasets
    total_samples = real_count + fake_count
    if total_samples < 20:
        batch_size = 1  # Use batch size 1 for very small datasets
    elif total_samples < 50:
        batch_size = 4
    else:
        batch_size = 16
    
    data = data.shuffle(buffer_size=min(2100, total_samples * 2))
    data = data.batch(batch_size=batch_size)
    data = data.prefetch(buffer_size=8)
    
    print("  ✅ Dataset prepared successfully!")
    return data


# ============================================================================
# STEP 4: Create Model
# ============================================================================

def create_model(input_shape=(128, 469, 1)):
    """Create the CNN model."""
    print("Step 3: Creating model...")
    
    # Use Input layer to properly define input shape
    model = Sequential([
        Input(shape=input_shape),
        Conv2D(filters=16, kernel_size=(3, 3), strides=(1, 1), 
               padding='same', activation='relu'),
        Conv2D(filters=16, kernel_size=(3, 3), strides=(1, 1), 
               padding='same', activation='relu'),
        tf.keras.layers.MaxPooling2D(pool_size=(2, 2), strides=(1, 1), 
                                     padding='valid'),
        Flatten(),
        Dense(units=32, activation='relu', use_bias=True),
        Dense(units=16, activation='relu', use_bias=True),
        Dense(units=1, activation='sigmoid', use_bias=True)
    ])
    
    model.compile(
        optimizer=tf.keras.optimizers.Adam(),
        loss=tf.keras.losses.BinaryCrossentropy(),
        metrics=['accuracy', 
                tf.keras.metrics.Precision(), 
                tf.keras.metrics.Recall()]
    )
    
    print("  ✅ Model created successfully!")
    model.summary()
    return model


# ============================================================================
# STEP 5: Train Model
# ============================================================================

def train_model(data, epochs=10):
    """Train the model."""
    print("Step 4: Training model...")
    
    # Split data (70% train, 30% test)
    data_list = list(data)
    data_size = len(data_list)
    train_size = int(data_size * 0.7)
    
    train = data.take(train_size)
    test = data.skip(train_size)
    
    print(f"  Training samples: {train_size}")
    print(f"  Test samples: {data_size - train_size}")
    
    # Create model
    model = create_model(input_shape=(128, 469, 1))
    
    # Train
    print("  Starting training (this will take a while)...")
    print("  Epochs:", epochs)
    history = model.fit(
        train, 
        validation_data=test, 
        epochs=epochs,
        verbose=1
    )
    
    # Evaluate
    print("Step 5: Evaluating model...")
    X_tests = []
    y = []
    for x_test, y_true in test.as_numpy_iterator():
        X_tests.append(x_test)
        y.append(y_true)
    
    X_tests = np.concatenate([X_tests[i][0:] for i in range(len(X_tests))], axis=0)
    y_test = np.concatenate([y[i][0:] for i in range(len(y))], axis=0)
    
    test_results = model.evaluate(X_tests, y_test, return_dict=True, verbose=0)
    print("  Test Results:", test_results)
    
    return model, history, test_results


# ============================================================================
# STEP 6: Save Model
# ============================================================================

def save_model(model, model_path='models/auralguard_model.h5'):
    """Save the trained model."""
    print("Step 6: Saving model...")
    
    os.makedirs(os.path.dirname(model_path), exist_ok=True)
    model.save(model_path)
    print(f"  ✅ Model saved to {model_path}")
    
    return model_path


# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main(epochs=10, skip_chunks=False):
    """Main training pipeline."""
    
    # Step 1: Prepare audio chunks (if needed)
    if not skip_chunks:
        if not prepare_audio_chunks():
            print("\n❌ Failed to prepare audio chunks. Exiting.")
            return None
    else:
        print("Skipping chunk preparation (using existing chunks)...")
    
    # Step 2: Prepare dataset
    data = prepare_dataset()
    if data is None:
        print("\n❌ Failed to prepare dataset. Exiting.")
        return None
    
    # Step 3 & 4: Create and train model
    model, history, test_results = train_model(data, epochs=epochs)
    
    # Step 5: Save model
    model_path = save_model(model)
    
    # Step 6: Log to MLflow (optional)
    try:
        print("Step 7: Logging to MLflow...")
        tracker = MLflowTracker()
        tracker.log_training_run(
            model=model,
            history=history,
            test_metrics=test_results,
            model_path=model_path,
            params={
                'epochs': epochs,
                'batch_size': 16,
                'input_shape': '(128, 469, 1)',
                'optimizer': 'Adam',
                'loss': 'BinaryCrossentropy'
            },
            tags={
                'model_type': 'CNN',
                'task': 'audio_authenticity_detection'
            }
        )
        print("  ✅ Logged to MLflow successfully!")
    except Exception as e:
        print(f"  ⚠️  Warning: MLflow logging failed: {e}")
    
    print()
    print("=" * 60)
    print("✅ Training Complete!")
    print("=" * 60)
    print(f"Model saved at: {model_path}")
    print("You can now deploy with: docker-compose up -d")
    print()
    
    return model, history, test_results


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Train AuralGuard model')
    parser.add_argument('--epochs', type=int, default=10, 
                       help='Number of training epochs (default: 10)')
    parser.add_argument('--skip-chunks', action='store_true',
                       help='Skip chunk creation if chunks already exist')
    
    args = parser.parse_args()
    
    print(f"Training configuration:")
    print(f"  Epochs: {args.epochs}")
    print(f"  Skip chunks: {args.skip_chunks}")
    print()
    
    main(epochs=args.epochs, skip_chunks=args.skip_chunks)

