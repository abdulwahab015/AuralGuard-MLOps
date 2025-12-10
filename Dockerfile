# Multi-stage Dockerfile for AuralGuard
FROM python:3.10-slim as base

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    make \
    libsndfile1 \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies with increased timeout and retry
# Install in batches to handle network timeouts better
RUN pip install --upgrade pip && \
    pip install --no-cache-dir --timeout=600 --retries=5 numpy pandas matplotlib seaborn scikit-learn && \
    pip install --no-cache-dir --timeout=600 --retries=5 librosa soundfile && \
    pip install --no-cache-dir --timeout=900 --retries=3 tensorflow tensorflow-io keras && \
    pip install --no-cache-dir --timeout=600 --retries=5 flask werkzeug pymongo mlflow python-dotenv

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p models uploads mlruns

# Expose port
EXPOSE 5000

# Set environment variables
ENV FLASK_APP=api/app.py
ENV PYTHONUNBUFFERED=1

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:5000/health')" || exit 1

# Run Flask app
CMD ["python", "api/app.py"]


