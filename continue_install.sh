#!/bin/bash

# Script to continue/resume dependency installation
# Handles network errors and retries failed packages

echo "============================================================"
echo "Resuming Dependency Installation"
echo "============================================================"
echo ""

# Increase timeout settings
export PIP_DEFAULT_TIMEOUT=600

# Function to install package with retry
install_with_retry() {
    local package=$1
    local max_retries=3
    local retry=0
    
    while [ $retry -lt $max_retries ]; do
        echo "Installing $package (attempt $((retry + 1))/$max_retries)..."
        pip3 install --timeout=600 --retries=3 "$package" && {
            echo "✅ Successfully installed $package"
            return 0
        }
        retry=$((retry + 1))
        if [ $retry -lt $max_retries ]; then
            echo "⚠️  Failed, retrying in 5 seconds..."
            sleep 5
        fi
    done
    
    echo "❌ Failed to install $package after $max_retries attempts"
    return 1
}

# Check what's already installed
echo "Checking installed packages..."
echo ""

# List of all required packages
PACKAGES=(
    "numpy>=1.24.0"
    "pandas>=2.0.0"
    "matplotlib>=3.7.0"
    "seaborn>=0.12.0"
    "scikit-learn>=1.3.0"
    "librosa>=0.10.0"
    "soundfile>=0.12.0"
    "tensorflow>=2.13.0"
    "tensorflow-io>=0.31.0"
    "keras>=2.13.0"
    "flask>=2.3.0"
    "werkzeug>=2.3.0"
    "pymongo>=4.5.0"
    "mlflow>=2.7.0"
    "python-dotenv>=1.0.0"
)

# Check which packages are missing
echo "Checking which packages need to be installed..."
MISSING_PACKAGES=()

for package in "${PACKAGES[@]}"; do
    # Extract package name (before >=)
    pkg_name=$(echo "$package" | cut -d'>' -f1 | cut -d'=' -f1)
    
    # Check if installed
    if ! python3 -c "import ${pkg_name//-/_}" 2>/dev/null; then
        MISSING_PACKAGES+=("$package")
        echo "  ❌ Missing: $pkg_name"
    else
        echo "  ✅ Installed: $pkg_name"
    fi
done

echo ""
echo "============================================================"
echo "Packages to install: ${#MISSING_PACKAGES[@]}"
echo "============================================================"
echo ""

if [ ${#MISSING_PACKAGES[@]} -eq 0 ]; then
    echo "✅ All packages are already installed!"
    exit 0
fi

# Install missing packages
FAILED_PACKAGES=()

# Install TensorFlow separately (it's the largest and most likely to timeout)
if [[ " ${MISSING_PACKAGES[@]} " =~ " tensorflow" ]]; then
    echo "Installing TensorFlow packages (this may take a while)..."
    echo ""
    
    install_with_retry "tensorflow>=2.13.0" || FAILED_PACKAGES+=("tensorflow>=2.13.0")
    install_with_retry "tensorflow-io>=0.31.0" || FAILED_PACKAGES+=("tensorflow-io>=0.31.0")
    install_with_retry "keras>=2.13.0" || FAILED_PACKAGES+=("keras>=2.13.0")
    
    echo ""
fi

# Install other packages
echo "Installing remaining packages..."
echo ""

for package in "${MISSING_PACKAGES[@]}"; do
    # Skip TensorFlow packages (already handled)
    if [[ "$package" == *"tensorflow"* ]] || [[ "$package" == *"keras"* ]]; then
        continue
    fi
    
    install_with_retry "$package" || FAILED_PACKAGES+=("$package")
    echo ""
done

# Summary
echo "============================================================"
echo "Installation Summary"
echo "============================================================"
echo ""

if [ ${#FAILED_PACKAGES[@]} -eq 0 ]; then
    echo "✅ All packages installed successfully!"
    echo ""
    echo "Next steps:"
    echo "  1. Train model: python3 complete_training.py --epochs 10"
    echo "  2. Deploy: docker-compose up -d"
else
    echo "⚠️  Some packages failed to install:"
    for pkg in "${FAILED_PACKAGES[@]}"; do
        echo "  - $pkg"
    done
    echo ""
    echo "You can retry installing them individually:"
    echo "  pip3 install --timeout=600 --retries=5 <package-name>"
    echo ""
    echo "Or run this script again to retry:"
    echo "  ./continue_install.sh"
fi

echo ""

