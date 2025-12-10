"""
Script to train the model and save it for deployment.
This extracts the training logic from the notebook.
"""

import tensorflow as tf
import os
import sys
from utils.model_loader import create_model
from utils.audio_processor import load_wav_16k_mono
from mlflow_tracking import MLflowTracker
import librosa
import numpy as np

# Note: This script assumes you have already created the audio chunks
# Run the notebook cells for data preparation first, or adapt this script
# to include the data preparation steps.


def file_to_mel_spectrogram_by_lib(filename, label):
    """Convert file to mel-spectrogram (from notebook)."""
    def numpy_func(filename_tensor):
        wav, samp_rate = librosa.load(
            filename_tensor.numpy().decode('utf-8'), 
            sr=16000, 
            mono=True
        )
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
    mel_spectrogram = tf.expand_dims(mel_spectrogram, axis=2)
    return mel_spectrogram, label


def prepare_dataset(real_chunks_path='real_audio_chunks', 
                   fake_chunks_path='fake_audio_chunks'):
    """Prepare TensorFlow dataset from audio chunks."""
    # Create datasets
    real_chunks_examples = tf.data.Dataset.list_files(
        os.path.join(real_chunks_path, '*.wav')
    )
    fake_chunks_examples = tf.data.Dataset.list_files(
        os.path.join(fake_chunks_path, '*.wav')
    )
    
    # Create labels
    real_labels = tf.data.Dataset.from_tensor_slices(
        tf.ones(len(list(real_chunks_examples)))
    )
    fake_labels = tf.data.Dataset.from_tensor_slices(
        tf.zeros(len(list(fake_chunks_examples)))
    )
    
    # Zip with labels
    real_data = tf.data.Dataset.zip((real_chunks_examples, real_labels))
    fake_data = tf.data.Dataset.zip((fake_chunks_examples, fake_labels))
    
    # Concatenate
    data = real_data.concatenate(fake_data)
    
    # Map to mel-spectrograms
    data = data.map(file_to_mel_spectrogram_by_lib)
    data = data.cache()
    data = data.shuffle(buffer_size=2100)
    data = data.batch(batch_size=16)
    data = data.prefetch(buffer_size=8)
    
    return data


def train_model(epochs=10, model_save_path='models/auralguard_model.h5'):
    """Train the model and save it."""
    print("Preparing dataset...")
    data = prepare_dataset()
    
    # Split data (70% train, 30% test)
    data_size = len(list(data))
    train_size = int(data_size * 0.7)
    
    train = data.take(train_size)
    test = data.skip(train_size)
    
    print(f"Training samples: {train_size}")
    print(f"Test samples: {data_size - train_size}")
    
    # Create model
    print("Creating model...")
    model = create_model(input_shape=(128, 469, 1))
    model.summary()
    
    # Train model
    print("Training model...")
    history = model.fit(
        train, 
        validation_data=test, 
        epochs=epochs,
        verbose=1
    )
    
    # Evaluate
    print("Evaluating model...")
    X_tests = []
    y = []
    for x_test, y_true in test.as_numpy_iterator():
        X_tests.append(x_test)
        y.append(y_true)
    
    X_tests = np.concatenate([X_tests[i][0:] for i in range(len(X_tests))], axis=0)
    y_test = np.concatenate([y[i][0:] for i in range(len(y))], axis=0)
    
    test_results = model.evaluate(X_tests, y_test, return_dict=True, verbose=0)
    print("Test Results:", test_results)
    
    # Save model
    os.makedirs(os.path.dirname(model_save_path), exist_ok=True)
    model.save(model_save_path)
    print(f"Model saved to {model_save_path}")
    
    # Log to MLflow
    try:
        tracker = MLflowTracker()
        tracker.log_training_run(
            model=model,
            history=history,
            test_metrics=test_results,
            model_path=model_save_path,
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
    except Exception as e:
        print(f"Warning: MLflow logging failed: {e}")
    
    return model, history, test_results


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Train AuralGuard model')
    parser.add_argument('--epochs', type=int, default=10, 
                       help='Number of training epochs')
    parser.add_argument('--model-path', type=str, 
                       default='models/auralguard_model.h5',
                       help='Path to save the model')
    
    args = parser.parse_args()
    
    train_model(epochs=args.epochs, model_save_path=args.model_path)


