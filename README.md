# 🎙️ AuralGuard: CNN Framework for Audio Authenticity Detection

A fully functional MLOps system to classify AI-generated or human audios. This project includes a complete deployment pipeline with Flask REST API, MLflow tracking, MongoDB logging, Docker containerization, and cloud deployment capabilities.

<details>
<summary>Table of Contents</summary>

- [Overview](#overview)
- [Features](#features)
- [Project Structure](#project-structure)
- [Quick Start](#quick-start)
- [Requirements](#requirements)
- [Model Architecture](#model-architecture)
- [API Documentation](#api-documentation)
- [Deployment](#deployment)
- [MLOps Stack](#mlops-stack)
- [Model Performance](#model-performance)
- [Contributing](#contributing)

</details>

## Overview

AuralGuard is a production-ready MLOps system for detecting AI-generated audio. The system extracts relevant features from raw audio (spectrograms, mel-spectrograms, and MFCCs) and uses a CNN model to classify audio as authentic or AI-generated.

**Key Features:**
- 🎯 CNN-based audio authenticity classification
- 🚀 RESTful API with Flask
- 📊 MLflow experiment tracking and model versioning
- 💾 MongoDB for prediction logging and analytics
- 🐳 Docker containerization for easy deployment
- ☁️ Cloud deployment ready (AWS, Railway, Render)
- 🔍 Real-time prediction with confidence scores

## Features

### Model Features
- **Feature Extraction**: Mel-spectrograms (128 mel bands, 8kHz max frequency)
- **Preprocessing**: 16kHz mono conversion, 15-second chunking
- **Architecture**: CNN with 2 Conv2D layers, MaxPooling, and Dense layers
- **Input Shape**: (128, 469, 1) mel-spectrogram tensors

### MLOps Features
- **REST API**: Flask-based API with `/predict`, `/health`, `/statistics` endpoints
- **Model Tracking**: MLflow integration for experiment tracking
- **Data Logging**: MongoDB integration for prediction history
- **Containerization**: Docker and Docker Compose setup
- **Cloud Ready**: Deployment scripts for AWS, Railway, Render

## Requirements

### Python Dependencies
- Python 3.10+
- TensorFlow 2.13+
- Keras 2.13+
- Flask 2.3+
- MLflow 2.7+
- MongoDB (local or Atlas)
- See `requirements.txt` for complete list

### System Dependencies
- Docker & Docker Compose (for containerized deployment)
- MongoDB (or MongoDB Atlas account)
- Git (for version control)

### Installation

```bash
# Install Python packages
pip install -r requirements.txt

# Or using Docker (includes all dependencies)
docker-compose up -d
```

## Dataset

The dataset used in this project consists of audio files labeled as either real or fake. 

<details>
<summary>Click to view dataset structure</summary>

The data is loaded from a CSV file containing the following columns:

- `filename`: Name of the audio file
- `label`: 'fake' or 'real'

Example:

| filename | label |
|----------|-------|
| audio1.wav | real |
| audio2.wav | fake |
| audio3.wav | real |

</details>

## Project Structure

```
MLOps Project/
├── api/
│   ├── __init__.py
│   └── app.py                 # Flask REST API
├── utils/
│   ├── __init__.py
│   ├── audio_processor.py    # Audio preprocessing utilities
│   ├── model_loader.py       # Model loading and prediction
│   └── database.py           # MongoDB integration
├── models/                    # Saved model files (gitignored)
├── mlruns/                    # MLflow tracking data (gitignored)
├── Audio_Detection.ipynb      # Original training notebook
├── train_and_save_model.py   # Training script
├── mlflow_tracking.py        # MLflow integration
├── test_api.py               # API testing script
├── requirements.txt          # Python dependencies
├── Dockerfile                # Docker image definition
├── docker-compose.yml        # Multi-container setup
└── README.md                 # This file
```

## Quick Start

### Quick Start (Docker - Recommended)

```bash
# 1. Save your model from notebook
# In Audio_Detection.ipynb, after training:
import os
os.makedirs('models', exist_ok=True)
model.save('models/auralguard_model.h5')

# 2. Start everything with Docker
docker-compose up -d

# 3. Test it
curl http://localhost:5000/health
```

**That's it!** Your API is running at http://localhost:5000

### Alternative: Local Setup (Without Docker)

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Train model (or use existing)
python train_and_save_model.py --epochs 10

# 3. Start MongoDB (optional)
docker run -d -p 27017:27017 --name mongodb mongo:7.0

# 4. Run API
python api/app.py

# 5. Test
curl http://localhost:5000/health
```

See the Quick Start section above for instructions.

## Model Architecture

```
Input: Audio File (WAV, MP3, etc.)
  ↓
Preprocessing: 16kHz Mono Conversion
  ↓
Feature Extraction: Mel-Spectrogram (128×469×1)
  ↓
CNN Layers:
  - Conv2D(16 filters, 3×3) + ReLU
  - Conv2D(16 filters, 3×3) + ReLU
  - MaxPooling2D(2×2)
  - Flatten
  - Dense(32) + ReLU
  - Dense(16) + ReLU
  - Dense(1) + Sigmoid
  ↓
Output: Probability (0-1) → Label (Real/Fake)
```

## API Documentation

### Endpoints

- `GET /health` - Health check and system status
- `POST /predict` - Predict audio authenticity (accepts audio file)
- `GET /statistics` - Get prediction statistics
- `GET /predictions?limit=N` - Get recent predictions

### Example Request

```bash
curl -X POST \
  -F "audio=@test_audio.wav" \
  http://localhost:5000/predict
```

### Example Response

```json
{
  "prediction": "real",
  "probability": 0.9234,
  "confidence": 0.8468,
  "filename": "test_audio.wav",
  "processing_time_seconds": 0.1234,
  "timestamp": "2024-01-01T00:00:00"
}
```

## Deployment

### Local Deployment
See the Quick Start section above for instructions.

### Docker Deployment
```bash
docker-compose up -d
```

### Cloud Deployment
- **AWS**: EC2, ECS, Lambda
- **Railway.app**: Free tier available
- **Render.com**: Free tier available

For cloud deployment, follow the Docker setup instructions and deploy the containerized application to your preferred cloud platform.

## MLOps Stack

This project demonstrates a complete MLOps pipeline:

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Model Training** | TensorFlow/Keras | CNN model development |
| **API Framework** | Flask | REST API for predictions |
| **Model Tracking** | MLflow | Experiment tracking & versioning |
| **Database** | MongoDB | Prediction logging & analytics |
| **Containerization** | Docker | Consistent deployment |
| **Orchestration** | Docker Compose | Multi-container setup |
| **Version Control** | Git/DagsHub | Code & data versioning |
| **Cloud** | AWS/Railway/Render | Scalable deployment |

## Model Performance

The current model achieves the following performance:

- **Training Accuracy**: 99.42% 🎉
- **Validation Accuracy**: 98.75% 🌟
- **Test Accuracy**: 99.14% ⭐
- **Precision**: 93.24%
- **Recall**: 100%

These results indicate that the model is highly effective at distinguishing between real and fake audio samples.

## Contributing

We welcome contributions! Here's how you can help:

1. 🍴 Fork the repository
2. 🌿 Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. 🔧 Make your changes
4. 📝 Commit your changes (`git commit -m 'Add some AmazingFeature'`)
5. 🚀 Push to the branch (`git push origin feature/AmazingFeature`)
6. 🔀 Open a Pull Request

## License

This project is part of an MLOps course assignment. Feel free to use and modify for educational purposes.

## Acknowledgments

- Course: Machine Learning Operations
- Technologies: Python, TensorFlow, Flask, MLflow, MongoDB, Docker, AWS

