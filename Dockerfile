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
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
# Use requirements.txt for better dependency resolution
# Increased timeout and retries for network issues
RUN pip install --upgrade pip setuptools wheel && \
    pip install --no-cache-dir \
        --timeout=900 \
        --retries=10 \
        --default-timeout=900 \
        --trusted-host pypi.org \
        --trusted-host files.pythonhosted.org \
        -r requirements.txt || \
    (echo "First attempt failed, retrying..." && \
     pip install --no-cache-dir \
         --timeout=1200 \
         --retries=15 \
         --default-timeout=1200 \
         --trusted-host pypi.org \
         --trusted-host files.pythonhosted.org \
         -r requirements.txt)

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


