"""
MLflow integration for experiment tracking and model versioning.
"""

import mlflow
import mlflow.keras
import os
from datetime import datetime


class MLflowTracker:
    """Handles MLflow experiment tracking."""
    
    def __init__(self, experiment_name: str = "AuralGuard"):
        """
        Initialize MLflow tracking.
        
        Args:
            experiment_name: Name of the MLflow experiment
        """
        # Set tracking URI (can be local or remote)
        tracking_uri = os.getenv('MLFLOW_TRACKING_URI', 'file:./mlruns')
        mlflow.set_tracking_uri(tracking_uri)
        
        # Set or create experiment
        try:
            experiment = mlflow.get_experiment_by_name(experiment_name)
            if experiment is None:
                experiment_id = mlflow.create_experiment(experiment_name)
            else:
                experiment_id = experiment.experiment_id
        except Exception as e:
            print(f"Warning: Could not set up MLflow experiment: {e}")
            experiment_id = "0"
        
        mlflow.set_experiment(experiment_name)
        self.experiment_name = experiment_name
    
    def log_training_run(self,
                        model,
                        history,
                        test_metrics: dict,
                        model_path: str = None,
                        params: dict = None,
                        tags: dict = None):
        """
        Log a training run to MLflow.
        
        Args:
            model: Trained Keras model
            history: Training history object
            test_metrics: Dictionary of test metrics
            model_path: Path to save the model
            params: Hyperparameters to log
            tags: Additional tags
        """
        try:
            with mlflow.start_run():
                # Log parameters
                if params:
                    mlflow.log_params(params)
                
                # Log tags
                if tags:
                    mlflow.set_tags(tags)
                
                # Log training metrics
                if history:
                    for epoch, (loss, acc) in enumerate(
                        zip(history.history['loss'], 
                            history.history['accuracy']), 
                        start=1
                    ):
                        mlflow.log_metric('train_loss', loss, step=epoch)
                        mlflow.log_metric('train_accuracy', acc, step=epoch)
                    
                    if 'val_loss' in history.history:
                        for epoch, (val_loss, val_acc) in enumerate(
                            zip(history.history['val_loss'],
                                history.history['val_accuracy']),
                            start=1
                        ):
                            mlflow.log_metric('val_loss', val_loss, step=epoch)
                            mlflow.log_metric('val_accuracy', val_acc, step=epoch)
                
                # Log test metrics
                for metric_name, metric_value in test_metrics.items():
                    mlflow.log_metric(f'test_{metric_name}', metric_value)
                
                # Log model
                if model_path:
                    mlflow.keras.log_model(model, "model", 
                                          registered_model_name="AuralGuard")
                else:
                    mlflow.keras.log_model(model, "model")
                
                print("Training run logged to MLflow successfully")
        
        except Exception as e:
            print(f"Warning: Could not log to MLflow: {e}")
    
    def log_model_deployment(self, model_path: str, deployment_info: dict):
        """
        Log model deployment information.
        
        Args:
            model_path: Path to deployed model
            deployment_info: Dictionary with deployment metadata
        """
        try:
            with mlflow.start_run(run_name="deployment"):
                mlflow.set_tags({
                    'deployment': 'true',
                    'deployment_timestamp': datetime.utcnow().isoformat(),
                    **deployment_info
                })
                mlflow.log_artifact(model_path, "deployed_model")
                print("Deployment logged to MLflow successfully")
        except Exception as e:
            print(f"Warning: Could not log deployment to MLflow: {e}")


def save_model_with_mlflow(model, model_path: str, metrics: dict = None):
    """
    Save model and optionally log to MLflow.
    
    Args:
        model: Keras model to save
        model_path: Path to save model
        metrics: Optional metrics to log
    """
    # Save model
    os.makedirs(os.path.dirname(model_path), exist_ok=True)
    model.save(model_path)
    print(f"Model saved to {model_path}")
    
    # Log to MLflow if metrics provided
    if metrics:
        tracker = MLflowTracker()
        tracker.log_model_deployment(model_path, metrics)


