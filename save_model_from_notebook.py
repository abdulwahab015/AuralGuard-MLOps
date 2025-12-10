"""
Helper script to save the trained model from the notebook.
Run this after training the model in Audio_Detection.ipynb
"""

import tensorflow as tf
import os
import sys

# Add utils to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.model_loader import create_model
from mlflow_tracking import MLflowTracker

def save_model_from_notebook(model, model_path='models/auralguard_model.h5'):
    """
    Save a trained model from the notebook.
    
    Usage in notebook:
        # After training
        from save_model_from_notebook import save_model_from_notebook
        save_model_from_notebook(model)
    
    Or run this script and it will prompt you to load the model.
    """
    # Create models directory if it doesn't exist
    os.makedirs(os.path.dirname(model_path), exist_ok=True)
    
    # Save model
    model.save(model_path)
    print(f"✅ Model saved successfully to {model_path}")
    
    # Log to MLflow
    try:
        tracker = MLflowTracker()
        tracker.log_model_deployment(
            model_path=model_path,
            deployment_info={
                'model_type': 'CNN',
                'input_shape': '(128, 469, 1)',
                'task': 'audio_authenticity_detection'
            }
        )
        print("✅ Model logged to MLflow")
    except Exception as e:
        print(f"⚠️  Warning: Could not log to MLflow: {e}")
    
    return model_path


if __name__ == '__main__':
    print("=" * 50)
    print("AuralGuard Model Saver")
    print("=" * 50)
    print()
    print("This script helps save your trained model.")
    print("You have two options:")
    print()
    print("Option 1: Use in Jupyter Notebook")
    print("  After training your model, run:")
    print("  from save_model_from_notebook import save_model_from_notebook")
    print("  save_model_from_notebook(model)")
    print()
    print("Option 2: Load and save model file")
    print("  If you have a saved model file, specify the path:")
    print()
    
    model_path = input("Enter path to model file (or press Enter to skip): ").strip()
    
    if model_path and os.path.exists(model_path):
        try:
            model = tf.keras.models.load_model(model_path)
            output_path = input("Enter output path (default: models/auralguard_model.h5): ").strip()
            if not output_path:
                output_path = 'models/auralguard_model.h5'
            
            save_model_from_notebook(model, output_path)
        except Exception as e:
            print(f"❌ Error: {e}")
    else:
        print("Please train the model in the notebook first, then use Option 1.")


