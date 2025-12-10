"""
Python script to check and install missing dependencies.
More reliable than shell script for package checking.
"""

import subprocess
import sys
import time

# Required packages with their import names
REQUIRED_PACKAGES = {
    'numpy': 'numpy>=1.24.0',
    'pandas': 'pandas>=2.0.0',
    'matplotlib': 'matplotlib>=3.7.0',
    'seaborn': 'seaborn>=0.12.0',
    'sklearn': 'scikit-learn>=1.3.0',
    'librosa': 'librosa>=0.10.0',
    'soundfile': 'soundfile>=0.12.0',
    'tensorflow': 'tensorflow>=2.13.0',
    'tensorflow_io': 'tensorflow-io>=0.31.0',
    'keras': 'keras>=2.13.0',
    'flask': 'flask>=2.3.0',
    'werkzeug': 'werkzeug>=2.3.0',
    'pymongo': 'pymongo>=4.5.0',
    'mlflow': 'mlflow>=2.7.0',
    'dotenv': 'python-dotenv>=1.0.0',
}

def check_package_installed(package_name):
    """Check if a package is installed."""
    try:
        __import__(package_name)
        return True
    except ImportError:
        return False

def install_package(package_spec, max_retries=3):
    """Install a package with retry logic."""
    for attempt in range(1, max_retries + 1):
        print(f"  Installing {package_spec} (attempt {attempt}/{max_retries})...")
        try:
            result = subprocess.run(
                [sys.executable, '-m', 'pip', 'install', 
                 '--timeout=600', '--retries=3', package_spec],
                capture_output=True,
                text=True,
                timeout=900  # 15 minutes max per package
            )
            
            if result.returncode == 0:
                print(f"  ✅ Successfully installed {package_spec}")
                return True
            else:
                print(f"  ⚠️  Attempt {attempt} failed")
                if attempt < max_retries:
                    print(f"  Waiting 5 seconds before retry...")
                    time.sleep(5)
        except subprocess.TimeoutExpired:
            print(f"  ⚠️  Timeout on attempt {attempt}")
            if attempt < max_retries:
                print(f"  Retrying...")
                time.sleep(5)
        except Exception as e:
            print(f"  ⚠️  Error: {e}")
            if attempt < max_retries:
                time.sleep(5)
    
    print(f"  ❌ Failed to install {package_spec} after {max_retries} attempts")
    return False

def main():
    print("=" * 60)
    print("Dependency Installation Checker")
    print("=" * 60)
    print()
    
    # Check installed packages
    print("Checking installed packages...")
    print()
    
    installed = []
    missing = []
    
    for import_name, package_spec in REQUIRED_PACKAGES.items():
        if check_package_installed(import_name):
            print(f"  ✅ {import_name} - installed")
            installed.append(import_name)
        else:
            print(f"  ❌ {import_name} - missing")
            missing.append(package_spec)
    
    print()
    print("=" * 60)
    print(f"Summary: {len(installed)} installed, {len(missing)} missing")
    print("=" * 60)
    print()
    
    if not missing:
        print("✅ All packages are already installed!")
        print()
        print("Next steps:")
        print("  1. Train model: python3 complete_training.py --epochs 10")
        print("  2. Deploy: docker-compose up -d")
        return
    
    # Install missing packages
    print(f"Installing {len(missing)} missing packages...")
    print()
    
    # Install TensorFlow packages first (they're largest)
    tensorflow_packages = [p for p in missing if 'tensorflow' in p or 'keras' in p]
    other_packages = [p for p in missing if p not in tensorflow_packages]
    
    failed = []
    
    # Install TensorFlow packages separately
    if tensorflow_packages:
        print("Installing TensorFlow packages (this may take a while)...")
        print()
        for package in tensorflow_packages:
            if not install_package(package):
                failed.append(package)
            print()
    
    # Install other packages
    if other_packages:
        print("Installing other packages...")
        print()
        for package in other_packages:
            if not install_package(package):
                failed.append(package)
            print()
    
    # Summary
    print("=" * 60)
    print("Installation Complete")
    print("=" * 60)
    print()
    
    if not failed:
        print("✅ All packages installed successfully!")
        print()
        print("Next steps:")
        print("  1. Train model: python3 complete_training.py --epochs 10")
        print("  2. Deploy: docker-compose up -d")
    else:
        print(f"⚠️  {len(failed)} package(s) failed to install:")
        for pkg in failed:
            print(f"  - {pkg}")
        print()
        print("You can retry installing them:")
        print("  pip3 install --timeout=600 --retries=5 <package-name>")
        print()
        print("Or run this script again:")
        print("  python3 install_missing.py")

if __name__ == '__main__':
    main()

