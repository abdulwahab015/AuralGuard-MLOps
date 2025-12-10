"""
Script to check training status and monitor progress.
"""

import os
import subprocess
import sys
from pathlib import Path
from datetime import datetime

def check_training_process():
    """Check if training process is running."""
    try:
        result = subprocess.run(
            ['ps', 'aux'],
            capture_output=True,
            text=True
        )
        
        processes = result.stdout
        if 'complete_training.py' in processes or 'python' in processes:
            # Check more specifically
            result = subprocess.run(
                ['pgrep', '-f', 'complete_training'],
                capture_output=True
            )
            if result.returncode == 0:
                return True, "Training process is running"
        return False, "No training process found"
    except:
        return False, "Could not check process"

def check_model_file():
    """Check if model file exists."""
    model_path = Path('models/auralguard_model.h5')
    if model_path.exists():
        size_mb = model_path.stat().st_size / (1024 * 1024)
        mtime = datetime.fromtimestamp(model_path.stat().st_mtime)
        return True, f"Model exists ({size_mb:.1f} MB, modified: {mtime.strftime('%Y-%m-%d %H:%M:%S')})"
    return False, "Model file not found"

def check_mlflow_runs():
    """Check MLflow runs directory."""
    mlruns_path = Path('mlruns')
    if mlruns_path.exists():
        runs = list(mlruns_path.glob('*/*/'))
        if runs:
            return True, f"Found {len(runs)} MLflow run(s)"
    return False, "No MLflow runs found"

def main():
    print("=" * 60)
    print("Training Status Checker")
    print("=" * 60)
    print()
    
    # Check process
    process_running, process_msg = check_training_process()
    print(f"Process Status: {process_msg}")
    if process_running:
        print("  ✅ Training is running in the background")
    else:
        print("  ⏳ No active training process")
    print()
    
    # Check model file
    model_exists, model_msg = check_model_file()
    print(f"Model File: {model_msg}")
    if model_exists:
        print("  ✅ Training completed! Model is saved")
    else:
        print("  ⏳ Model not created yet - training may still be in progress")
    print()
    
    # Check MLflow
    mlflow_exists, mlflow_msg = check_mlflow_runs()
    print(f"MLflow: {mlflow_msg}")
    print()
    
    # Summary
    print("=" * 60)
    if model_exists:
        print("✅ TRAINING COMPLETE!")
        print()
        print("Next steps:")
        print("  1. Deploy: docker-compose up -d")
        print("  2. Test: curl http://localhost:5000/health")
    elif process_running:
        print("⏳ TRAINING IN PROGRESS")
        print()
        print("The model is currently training. This may take 10-20 minutes.")
        print("Run this script again to check status:")
        print("  python3 check_training_status.py")
    else:
        print("❓ STATUS UNCERTAIN")
        print()
        print("Training may have completed or not started.")
        print("Check for model file: ls models/auralguard_model.h5")
        print("Or start training: python3 complete_training.py --epochs 10")
    print("=" * 60)

if __name__ == '__main__':
    main()

