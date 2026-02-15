"""
AI Security Risk Prediction API
Production-ready Flask application for security risk assessment
"""

from flask import Flask, request, jsonify
from datetime import datetime
import joblib
import numpy as np
import json
import os
import logging

# ============================================================================
# CONFIGURATION
# ============================================================================

app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Define required feature fields for predictions
REQUIRED_FIELDS = [
    "failed_login_attempts",
    "login_time_deviation",
    "ip_change",
    "device_change",
    "transaction_amount_deviation"
]

# ============================================================================
# MODEL LOADING
# ============================================================================

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
model_path = os.path.join(BASE_DIR, "model", "model.pkl")

try:
    model = joblib.load(model_path)
    logger.info(f"Model loaded successfully from {model_path}")
except FileNotFoundError:
    logger.error(f"Model file not found at {model_path}")
    model = None
except Exception as e:
    logger.error(f"Error loading model: {str(e)}")
    model = None


# ============================================================================
# MIDDLEWARE
# ============================================================================

@app.before_request
def handle_content_type():
    """Ensure Content-Type is set to application/json for POST requests"""
    if request.method == 'POST':
        if request.data and not request.is_json:
            request.environ['CONTENT_TYPE'] = 'application/json'


@app.after_request
def set_response_headers(response):
    """Set response headers for all responses"""
    response.headers['Content-Type'] = 'application/json'
    return response


# ============================================================================
# VALIDATION FUNCTIONS
# ============================================================================

def validate_request_body():
    """
    Validate that request has a body.
    
    Returns:
        tuple: (data_dict or None, error_message or None, status_code or None)
    """
    if not request.data:
        return None, "Request body is missing", 400
    
    return True, None, None


def validate_json_format():
    """
    Validate that request body is valid JSON.
    
    Returns:
        tuple: (data_dict or None, error_message or None, status_code or None)
    """
    try:
        if request.is_json:
            data = request.json
        else:
            data = json.loads(request.data.decode('utf-8'))
        
        if not isinstance(data, dict):
            return None, "JSON body must be an object/dictionary", 400
        
        return data, None, None
    
    except json.JSONDecodeError as e:
        return None, "Invalid JSON format in request body", 400
    except Exception as e:
        return None, "Error parsing request body", 400


def validate_required_fields(data):
    """
    Validate that all required fields are present in the data.
    
    Args:
        data (dict): Request data dictionary
    
    Returns:
        tuple: (True or False, error_message or None, status_code or None)
    """
    if not data:
        return False, "Request data is empty", 400
    
    # Check for missing fields
    missing_fields = [field for field in REQUIRED_FIELDS if field not in data]
    if missing_fields:
        if len(missing_fields) == 1:
            return False, f"Missing required field: {missing_fields[0]}", 400
        else:
            return False, f"Missing required fields: {', '.join(missing_fields)}", 400
    
    return True, None, None


def validate_field_types(data):
    """
    Validate that all fields have numeric values.
    
    Args:
        data (dict): Request data dictionary
    
    Returns:
        tuple: (True or False, error_message or None, status_code or None)
    """
    for field in REQUIRED_FIELDS:
        value = data.get(field)
        
        # Check if value is numeric (int or float)
        if not isinstance(value, (int, float)) or isinstance(value, bool):
            return False, f"Field '{field}' must be numeric (received: {type(value).__name__})", 400
    
    return True, None, None


def validate_prediction_input(data):
    """
    Comprehensive validation of prediction input.
    
    Args:
        data (dict): Request data dictionary
    
    Returns:
        tuple: (features_array or None, error_message or None, status_code or None)
    """
    # Validate required fields presence
    is_valid, error_msg, status = validate_required_fields(data)
    if not is_valid:
        return None, error_msg, status
    
    # Validate field types
    is_valid, error_msg, status = validate_field_types(data)
    if not is_valid:
        return None, error_msg, status
    
    # Extract and convert to numpy array
    try:
        features = [
            data["failed_login_attempts"],
            data["login_time_deviation"],
            data["ip_change"],
            data["device_change"],
            data["transaction_amount_deviation"]
        ]
        features_array = np.array([features])
        return features_array, None, None
    
    except Exception as e:
        logger.error(f"Error preparing features: {str(e)}")
        return None, "Error processing input features", 500


# ============================================================================
# ROUTES
# ============================================================================

@app.route("/", methods=["GET"])
def health_check():
    """
    Health check endpoint - confirms API is running and operational.
    
    Returns:
        JSON: Health status with timestamp and model status
        Status: 200 OK
    """
    return jsonify({
        "message": "AI Security Risk API is running",
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "model_loaded": model is not None,
        "version": "1.0.0"
    }), 200


@app.route("/health", methods=["GET"])
def health():
    """Alias for health check endpoint"""
    return health_check()


@app.route("/predict", methods=["POST"])
def predict():
    """
    Predict security risk based on input features.
    
    Expected JSON body:
    {
        "failed_login_attempts": float,
        "login_time_deviation": float,
        "ip_change": int,
        "device_change": int,
        "transaction_amount_deviation": float
    }
    
    Returns:
        JSON: Prediction result with risk_label, risk_score, and status
        Status: 200 OK on success, 400 on client error, 500 on server error
    """
    
    try:
        # Step 1: Validate request body exists
        is_valid, error_msg, status = validate_request_body()
        if not is_valid:
            return jsonify({"error": error_msg}), status
        
        # Step 2: Validate JSON format
        data, error_msg, status = validate_json_format()
        if data is None:
            return jsonify({"error": error_msg}), status
        
        # Step 3: Validate and prepare input
        features_array, error_msg, status = validate_prediction_input(data)
        if features_array is None:
            return jsonify({"error": error_msg}), status
        
        # Step 4: Check model is loaded
        if model is None:
            logger.error("Model is not loaded")
            return jsonify({"error": "Internal server error"}), 500
        
        # Step 5: Make prediction
        prediction = model.predict(features_array)[0]
        probability = model.predict_proba(features_array)[0][1]
        
        # Step 6: Format response
        response = {
            "risk_label": int(prediction),
            "risk_score": round(float(probability) * 100, 2),
            "status": "High Risk" if prediction == 1 else "Safe"
        }
        
        logger.info(f"Prediction made - Risk Label: {prediction}, Risk Score: {response['risk_score']}%")
        return jsonify(response), 200
    
    except Exception as e:
        # Log the actual error but don't expose it to client
        logger.error(f"Unexpected error in /predict endpoint: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500


# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.errorhandler(404)
def not_found(error):
    """Handle 404 Not Found errors"""
    return jsonify({"error": "Endpoint not found"}), 404


@app.errorhandler(405)
def method_not_allowed(error):
    """Handle 405 Method Not Allowed errors"""
    return jsonify({"error": "Method not allowed for this endpoint"}), 405


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 Internal Server errors"""
    logger.error(f"Internal server error: {str(error)}")
    return jsonify({"error": "Internal server error"}), 500


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    logger.info("Starting AI Security Risk Prediction API")
    app.run(
        debug=True,
        host='127.0.0.1',
        port=5000,
        threaded=True
    )
