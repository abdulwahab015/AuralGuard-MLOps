"""
Model loading utilities for AuralGuard.
Handles loading saved models and creating model architecture.
"""

import tensorflow as tf
from keras import Sequential
from keras.layers import Dense, Conv2D, Flatten
import os


def create_model(input_shape=(128, 469, 1)):
    """
    Create the CNN model architecture for audio authenticity detection.
    
    Args:
        input_shape: Shape of input mel-spectrogram (height, width, channels)
    
    Returns:
        model: Compiled Keras model
    """
    model = Sequential([
        Conv2D(filters=16, kernel_size=(3, 3), strides=(1, 1), 
               padding='same', activation='relu', 
               input_shape=input_shape),
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
    
    return model


def load_model(model_path):
    """
    Load a saved model from file.
    
    Args:
        model_path: Path to saved model (h5 or SavedModel format)
    
    Returns:
        model: Loaded Keras model
    """
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Model file not found: {model_path}")
    
    try:
        model = tf.keras.models.load_model(model_path)
        return model
    except Exception as e:
        raise Exception(f"Error loading model: {str(e)}")


def predict_audio(model, mel_spectrogram):
    """
    Make prediction on preprocessed audio.
    
    Args:
        model: Loaded Keras model
        mel_spectrogram: Preprocessed mel-spectrogram tensor
    
    Returns:
        prediction: Probability score (0-1), where 1 = real, 0 = fake
        label: String label ('real' or 'fake')
    """
    prediction = model.predict(mel_spectrogram, verbose=0)
    probability = float(prediction[0][0])
    label = 'real' if probability >= 0.5 else 'fake'
    
    return probability, label


