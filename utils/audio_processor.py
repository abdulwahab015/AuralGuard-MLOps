"""
Audio preprocessing utilities for AuralGuard model.
Extracts mel-spectrograms from audio files for CNN input.
"""

import tensorflow as tf
import tensorflow_io as tfio
import librosa
import numpy as np


def load_wav_16k_mono(filename):
    """
    Load audio file and convert to 16kHz mono waveform.
    
    Args:
        filename: Path to audio file (string or tensor)
    
    Returns:
        wav: TensorFlow tensor of audio waveform at 16kHz mono
    """
    # Handle both string paths and tensor paths
    if isinstance(filename, str):
        wav = tf.io.read_file(filename)
    else:
        wav = tf.io.read_file(filename)
    
    # Decode waveform from file contents. Channel 1 for mono audio.
    wav, sr = tf.audio.decode_wav(wav, desired_channels=1)
    
    # Remove trailing axis
    wav = tf.squeeze(wav, axis=1)
    
    # Change dtype of sampling rate
    sr = tf.cast(sr, dtype=tf.int64)
    
    # Resample to 16kHz
    wav = tfio.audio.resample(wav, rate_in=sr, rate_out=16000)
    
    return wav


def audio_to_mel_spectrogram(audio_path, max_length=240000):
    """
    Convert audio file to mel-spectrogram for model input.
    
    Args:
        audio_path: Path to audio file (string or bytes)
        max_length: Maximum length of waveform (default: 240000 for 15 seconds at 16kHz)
    
    Returns:
        mel_spectrogram: TensorFlow tensor of shape (128, 469, 1)
    """
    # Handle both string and bytes input (for Flask file uploads)
    if isinstance(audio_path, bytes):
        # Save bytes to temporary file
        import tempfile
        import os
        with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as tmp_file:
            tmp_file.write(audio_path)
            tmp_path = tmp_file.name
        
        try:
            wav, samp_rate = librosa.load(tmp_path, sr=16000, mono=True)
        finally:
            os.unlink(tmp_path)
    else:
        # Handle string path
        if isinstance(audio_path, tf.Tensor):
            audio_path = audio_path.numpy().decode('utf-8')
        wav, samp_rate = librosa.load(audio_path, sr=16000, mono=True)
    
    # Truncate or pad to max_length
    if len(wav) > max_length:
        wav = wav[:max_length]
    elif len(wav) < max_length:
        # Zero pad at the end
        padding = np.zeros(max_length - len(wav))
        wav = np.concatenate([wav, padding])
    
    # Generate mel-spectrogram
    mel_spectrogram = librosa.feature.melspectrogram(
        y=wav, 
        sr=samp_rate, 
        n_mels=128, 
        fmax=8000
    )
    
    # Convert to tensor and add channel dimension
    mel_spectrogram_tf = tf.convert_to_tensor(mel_spectrogram, dtype=tf.float32)
    mel_spectrogram_tf = tf.expand_dims(mel_spectrogram_tf, axis=2)
    
    return mel_spectrogram_tf


def preprocess_audio_for_prediction(audio_path):
    """
    Complete preprocessing pipeline for prediction.
    
    Args:
        audio_path: Path to audio file or bytes
    
    Returns:
        mel_spectrogram: Preprocessed mel-spectrogram ready for model input
    """
    mel_spec = audio_to_mel_spectrogram(audio_path)
    # Add batch dimension for model prediction
    mel_spec = tf.expand_dims(mel_spec, axis=0)
    return mel_spec

