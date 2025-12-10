"""
MongoDB integration for logging predictions and requests.
"""

from pymongo import MongoClient
from datetime import datetime
import os
from typing import Dict, Optional


class PredictionLogger:
    """Handles logging predictions to MongoDB."""
    
    def __init__(self, connection_string: Optional[str] = None):
        """
        Initialize MongoDB connection.
        
        Args:
            connection_string: MongoDB connection string. 
                              If None, uses MONGODB_URI environment variable.
        """
        self.connection_string = connection_string or os.getenv(
            'MONGODB_URI', 
            'mongodb://localhost:27017/'
        )
        self.db_name = os.getenv('MONGODB_DB_NAME', 'auralguard')
        self.collection_name = os.getenv('MONGODB_COLLECTION', 'predictions')
        
        try:
            self.client = MongoClient(self.connection_string)
            self.db = self.client[self.db_name]
            self.collection = self.db[self.collection_name]
            # Test connection
            self.client.admin.command('ping')
        except Exception as e:
            print(f"Warning: Could not connect to MongoDB: {e}")
            print("Predictions will not be logged to database.")
            self.client = None
            self.collection = None
    
    def log_prediction(self, 
                      audio_filename: str,
                      prediction: float,
                      label: str,
                      processing_time: float,
                      metadata: Optional[Dict] = None):
        """
        Log a prediction to MongoDB.
        
        Args:
            audio_filename: Name of the audio file
            prediction: Prediction probability (0-1)
            label: Predicted label ('real' or 'fake')
            processing_time: Time taken to process (seconds)
            metadata: Additional metadata to store
        """
        if self.collection is None:
            return
        
        document = {
            'timestamp': datetime.utcnow(),
            'audio_filename': audio_filename,
            'prediction_probability': prediction,
            'predicted_label': label,
            'processing_time_seconds': processing_time,
            'metadata': metadata or {}
        }
        
        try:
            self.collection.insert_one(document)
        except Exception as e:
            print(f"Error logging prediction to MongoDB: {e}")
    
    def get_recent_predictions(self, limit: int = 10):
        """
        Retrieve recent predictions from database.
        
        Args:
            limit: Number of recent predictions to retrieve
        
        Returns:
            List of prediction documents
        """
        if self.collection is None:
            return []
        
        try:
            predictions = list(
                self.collection.find()
                .sort('timestamp', -1)
                .limit(limit)
            )
            # Convert ObjectId to string for JSON serialization
            for pred in predictions:
                pred['_id'] = str(pred['_id'])
                if 'timestamp' in pred:
                    pred['timestamp'] = pred['timestamp'].isoformat()
            return predictions
        except Exception as e:
            print(f"Error retrieving predictions: {e}")
            return []
    
    def get_statistics(self):
        """
        Get statistics about predictions.
        
        Returns:
            Dictionary with prediction statistics
        """
        if self.collection is None:
            return {}
        
        try:
            total = self.collection.count_documents({})
            real_count = self.collection.count_documents({'predicted_label': 'real'})
            fake_count = self.collection.count_documents({'predicted_label': 'fake'})
            
            return {
                'total_predictions': total,
                'real_predictions': real_count,
                'fake_predictions': fake_count,
                'real_percentage': (real_count / total * 100) if total > 0 else 0,
                'fake_percentage': (fake_count / total * 100) if total > 0 else 0
            }
        except Exception as e:
            print(f"Error retrieving statistics: {e}")
            return {}


