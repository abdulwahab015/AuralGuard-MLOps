#!/bin/bash

# AuralGuard Setup Script
# This script helps set up the project environment

echo "=========================================="
echo "AuralGuard Setup Script"
echo "=========================================="
echo ""

# Check Python version
echo "Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "Python version: $python_version"

# Create virtual environment
echo ""
echo "Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install dependencies
echo ""
echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Create necessary directories
echo ""
echo "Creating directories..."
mkdir -p models
mkdir -p uploads
mkdir -p mlruns

# Copy environment file
if [ ! -f .env ]; then
    echo ""
    echo "Creating .env file from .env.example..."
    cp .env.example .env
    echo "⚠️  Please edit .env file with your configuration"
else
    echo ".env file already exists"
fi

echo ""
echo "=========================================="
echo "Setup complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Activate virtual environment: source venv/bin/activate"
echo "2. Train model: python train_and_save_model.py"
echo "3. Or use existing model at models/auralguard_model.h5"
echo "4. Start MongoDB (optional): docker run -d -p 27017:27017 --name mongodb mongo:7.0"
echo "5. Run API: python api/app.py"
echo ""
echo "Or use Docker: docker-compose up -d"
echo ""


