#!/bin/bash

# Script to install dependencies with retry and timeout handling
# This handles network timeouts better

echo "=" * 60
echo "Installing Dependencies with Retry Logic"
echo "=" * 60
echo ""

# Increase timeout for pip
export PIP_DEFAULT_TIMEOUT=300

# Install packages in smaller batches to avoid timeouts
echo "Installing core packages (batch 1/4)..."
pip3 install --timeout=300 --retries=5 numpy pandas matplotlib seaborn scikit-learn || echo "⚠️  Some packages failed, continuing..."

echo ""
echo "Installing audio processing packages (batch 2/4)..."
pip3 install --timeout=300 --retries=5 librosa soundfile || echo "⚠️  Some packages failed, continuing..."

echo ""
echo "Installing TensorFlow (batch 3/4) - This may take a while..."
pip3 install --timeout=600 --retries=3 tensorflow tensorflow-io keras || echo "⚠️  TensorFlow installation had issues, continuing..."

echo ""
echo "Installing web and database packages (batch 4/4)..."
pip3 install --timeout=300 --retries=5 flask werkzeug pymongo mlflow python-dotenv || echo "⚠️  Some packages failed, continuing..."

echo ""
echo "=" * 60
echo "Installation attempt complete!"
echo "=" * 60
echo ""
echo "If some packages failed, try installing them individually:"
echo "  pip3 install --timeout=600 <package-name>"

