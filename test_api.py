"""
Simple test script for the AuralGuard API.
"""

import requests
import os

API_URL = os.getenv('API_URL', 'http://localhost:5001')  # Changed to 5001 to avoid AirPlay conflict


def test_health():
    """Test health endpoint."""
    print("Testing /health endpoint...")
    response = requests.get(f"{API_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print()


def test_predict_file(audio_path):
    """Test prediction with file path."""
    print(f"Testing /predict endpoint with file: {audio_path}")
    
    if not os.path.exists(audio_path):
        print(f"Error: File not found: {audio_path}")
        return
    
    with open(audio_path, 'rb') as f:
        files = {'audio': (os.path.basename(audio_path), f, 'audio/wav')}
        response = requests.post(f"{API_URL}/predict", files=files)
    
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print()


def test_statistics():
    """Test statistics endpoint."""
    print("Testing /statistics endpoint...")
    response = requests.get(f"{API_URL}/statistics")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print()


def test_predictions():
    """Test predictions endpoint."""
    print("Testing /predictions endpoint...")
    response = requests.get(f"{API_URL}/predictions?limit=5")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print()


if __name__ == '__main__':
    import sys
    
    print("=" * 50)
    print("AuralGuard API Test Suite")
    print("=" * 50)
    print()
    
    # Test health
    try:
        test_health()
    except Exception as e:
        print(f"Health check failed: {e}")
        print("Make sure the API is running!")
        sys.exit(1)
    
    # Test prediction if audio file provided
    if len(sys.argv) > 1:
        audio_file = sys.argv[1]
        test_predict_file(audio_file)
    
    # Test statistics
    try:
        test_statistics()
    except Exception as e:
        print(f"Statistics test failed: {e}")
    
    # Test predictions
    try:
        test_predictions()
    except Exception as e:
        print(f"Predictions test failed: {e}")
    
    print("=" * 50)
    print("Tests completed!")
    print("=" * 50)


