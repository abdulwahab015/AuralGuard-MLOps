"""
Flask REST API for AuralGuard audio authenticity detection.
"""

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename
import os
import time
import traceback
from datetime import datetime

# Import utilities
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.model_loader import load_model, predict_audio
from utils.audio_processor import preprocess_audio_for_prediction
from utils.database import PredictionLogger

# Get the project root directory (parent of api/)
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
static_folder = os.path.join(project_root, 'static')

app = Flask(__name__, static_folder=static_folder, static_url_path='', template_folder=static_folder)
CORS(app)  # Enable CORS for all routes
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max file size
app.config['UPLOAD_FOLDER'] = os.getenv('UPLOAD_FOLDER', '/tmp/uploads')

# Initialize components
MODEL_PATH = os.getenv('MODEL_PATH', 'models/auralguard_model.h5')
model = None
db_logger = None

# Allowed audio extensions
ALLOWED_EXTENSIONS = {'wav', 'mp3', 'flac', 'ogg', 'm4a'}


def allowed_file(filename):
    """Check if file extension is allowed."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def initialize_model():
    """Load the model on startup."""
    global model
    try:
        if os.path.exists(MODEL_PATH):
            model = load_model(MODEL_PATH)
            print(f"Model loaded successfully from {MODEL_PATH}")
        else:
            print(f"Warning: Model file not found at {MODEL_PATH}")
            print("Please train and save the model first.")
    except Exception as e:
        print(f"Error loading model: {e}")
        traceback.print_exc()


def initialize_database():
    """Initialize MongoDB connection."""
    global db_logger
    try:
        db_logger = PredictionLogger()
        print("MongoDB connection initialized")
    except Exception as e:
        print(f"Warning: Database initialization failed: {e}")


@app.route('/', methods=['GET'])
def root():
    """Serve the frontend HTML page."""
    try:
        html_path = os.path.join(app.static_folder, 'index.html')
        if os.path.exists(html_path):
            return send_from_directory(app.static_folder, 'index.html')
        else:
            raise FileNotFoundError(f"HTML file not found at {html_path}")
    except Exception as e:
        # Fallback to JSON if HTML not found
        print(f"Error serving HTML: {e}")
        print(f"Static folder: {app.static_folder}")
        return jsonify({
            'message': 'AuralGuard API - Audio Authenticity Detection',
            'version': '1.0.0',
            'endpoints': {
                'health': '/health',
                'predict': '/predict',
                'statistics': '/statistics',
                'predictions': '/predictions?limit=N'
            },
            'status': 'running',
            'note': 'Frontend HTML not found'
        }), 200




@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'model_loaded': model is not None,
        'database_connected': db_logger is not None and db_logger.client is not None,
        'timestamp': datetime.utcnow().isoformat()
    }), 200


@app.route('/predict', methods=['POST'])
def predict():
    """
    Predict endpoint for audio authenticity detection.
    
    Accepts:
        - multipart/form-data with 'audio' file field
        - OR JSON with 'audio_path' field pointing to file
    
    Returns:
        JSON with prediction results
    """
    if model is None:
        return jsonify({
            'error': 'Model not loaded. Please ensure model file exists.'
        }), 500
    
    start_time = time.time()
    
    try:
        # Handle file upload
        if 'audio' in request.files:
            file = request.files['audio']
            if file.filename == '':
                return jsonify({'error': 'No file provided'}), 400
            
            if not allowed_file(file.filename):
                return jsonify({
                    'error': f'Invalid file type. Allowed: {", ".join(ALLOWED_EXTENSIONS)}'
                }), 400
            
            # Read file bytes
            audio_bytes = file.read()
            filename = secure_filename(file.filename)
            
            # Preprocess audio
            mel_spectrogram = preprocess_audio_for_prediction(audio_bytes)
            
        # Handle file path
        elif 'audio_path' in request.json:
            audio_path = request.json['audio_path']
            if not os.path.exists(audio_path):
                return jsonify({'error': 'File not found'}), 404
            
            filename = os.path.basename(audio_path)
            mel_spectrogram = preprocess_audio_for_prediction(audio_path)
        
        else:
            return jsonify({
                'error': 'Please provide either "audio" file or "audio_path" in request'
            }), 400
        
        # Make prediction
        probability, label = predict_audio(model, mel_spectrogram)
        
        processing_time = time.time() - start_time
        
        # Log to database
        if db_logger:
            db_logger.log_prediction(
                audio_filename=filename,
                prediction=probability,
                label=label,
                processing_time=processing_time,
                metadata={
                    'confidence': abs(probability - 0.5) * 2  # Convert to 0-1 confidence
                }
            )
        
        response = {
            'prediction': label,
            'probability': round(probability, 4),
            'confidence': round(abs(probability - 0.5) * 2, 4),
            'filename': filename,
            'processing_time_seconds': round(processing_time, 4),
            'timestamp': datetime.utcnow().isoformat()
        }
        
        return jsonify(response), 200
        
    except Exception as e:
        error_msg = str(e)
        print(f"Error in prediction: {error_msg}")
        traceback.print_exc()
        return jsonify({
            'error': 'Prediction failed',
            'message': error_msg
        }), 500


@app.route('/predictions', methods=['GET'])
def get_predictions():
    """Get recent predictions from database."""
    if db_logger is None:
        return jsonify({
            'error': 'Database not connected'
        }), 503
    
    try:
        limit = request.args.get('limit', 10, type=int)
        predictions = db_logger.get_recent_predictions(limit=limit)
        return jsonify({
            'predictions': predictions,
            'count': len(predictions)
        }), 200
    except Exception as e:
        return jsonify({
            'error': 'Failed to retrieve predictions',
            'message': str(e)
        }), 500


@app.route('/statistics', methods=['GET'])
def get_statistics():
    """Get prediction statistics."""
    if db_logger is None:
        return jsonify({
            'error': 'Database not connected'
        }), 503
    
    try:
        stats = db_logger.get_statistics()
        return jsonify(stats), 200
    except Exception as e:
        return jsonify({
            'error': 'Failed to retrieve statistics',
            'message': str(e)
        }), 500


@app.errorhandler(413)
def request_entity_too_large(error):
    """Handle file too large error."""
    return jsonify({
        'error': 'File too large. Maximum size is 50MB.'
    }), 413


if __name__ == '__main__':
    # Initialize on startup
    print("Initializing AuralGuard API...")
    initialize_model()
    initialize_database()
    
    # Run Flask app
    port = int(os.getenv('PORT', 5001))  # Changed default to 5001 to avoid AirPlay conflict
    debug = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    
    print(f"Starting Flask server on port {port}...")
    app.run(host='0.0.0.0', port=port, debug=debug)


