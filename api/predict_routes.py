"""
Prediction routes
Protected ML prediction endpoint with usage logging
"""

from flask import Blueprint, request, jsonify
from functools import wraps
import logging
from api.extensions import db
from api.models import User, APIUsageLog
from api.mongodb import find_user_by_api_key, increment_total_requests
import joblib
import numpy as np
import json
import logging

logger = logging.getLogger(__name__)

predict_bp = Blueprint('predict', __name__)

# Required feature fields for predictions
REQUIRED_FIELDS = [
    "failed_login_attempts",
    "login_time_deviation",
    "ip_change",
    "device_change",
    "transaction_amount_deviation"
]

# Global model variable (loaded in app.py)
model = None


def set_model(ml_model):
    """Set the ML model (called from app.py)"""
    global model
    model = ml_model


def require_api_key(f):
    """
    Decorator to require valid API key in x-api-key header.
    Checks MongoDB first (signup users), then SQLAlchemy (register users).
    Injects current_user and from_mongo into request context.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = (request.headers.get("x-api-key") or "").strip()
        if not api_key:
            return jsonify({"error": "API key required. Send it in the x-api-key header."}), 401

        # MongoDB (signup/login flow)
        user_mongo = find_user_by_api_key(api_key)
        if user_mongo:
            request.current_user = user_mongo
            request.from_mongo = True
            request._api_key = api_key
            return f(*args, **kwargs)

        # SQLAlchemy (register flow)
        user_sql = User.query.filter_by(api_key=api_key).first()
        if user_sql:
            request.current_user = user_sql
            request.from_mongo = False
            request._api_key = api_key
            return f(*args, **kwargs)

        return jsonify({"error": "Invalid or expired API key"}), 401
    return decorated_function


def validate_request_body():
    """Validate that request has a body"""
    if not request.data:
        return None, "Request body is missing", 400
    return True, None, None


def validate_json_format():
    """Validate and parse JSON request body"""
    try:
        if request.is_json:
            data = request.json
        else:
            data = json.loads(request.data.decode('utf-8'))
        
        if not isinstance(data, dict):
            return None, "JSON body must be an object/dictionary", 400
        
        return data, None, None
    except json.JSONDecodeError:
        return None, "Invalid JSON format in request body", 400
    except Exception as e:
        logger.error(f"JSON parsing error: {str(e)}")
        return None, "Error parsing request body", 400


def validate_required_fields(data):
    """Validate that all required fields are present"""
    if not data:
        return False, "Request data is empty", 400
    
    missing_fields = [field for field in REQUIRED_FIELDS if field not in data]
    if missing_fields:
        if len(missing_fields) == 1:
            return False, f"Missing required field: {missing_fields[0]}", 400
        else:
            return False, f"Missing required fields: {', '.join(missing_fields)}", 400
    
    return True, None, None


def validate_field_types(data):
    """Validate that all fields have numeric values"""
    for field in REQUIRED_FIELDS:
        value = data.get(field)
        
        # Check if value is numeric (int or float, but not bool)
        if not isinstance(value, (int, float)) or isinstance(value, bool):
            return False, f"Field '{field}' must be numeric (received: {type(value).__name__})", 400
    
    return True, None, None


def validate_prediction_input(data):
    """Comprehensive validation of prediction input"""
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


@predict_bp.route("/predict", methods=["POST"])
@require_api_key
def predict():
    """
    Predict security risk based on input features.
    Requires x-api-key header with valid API key.
    
    Request Headers:
        x-api-key: <your-api-key>
        Content-Type: application/json
    
    Request Body:
    {
        "failed_login_attempts": float,
        "login_time_deviation": float,
        "ip_change": int,
        "device_change": int,
        "transaction_amount_deviation": float
    }
    
    Returns:
        200: Prediction result with risk_label, risk_score, status
        400: Invalid input
        401: Missing or invalid API key
        500: Internal server error
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
        
        risk_label = int(prediction)
        risk_score = round(float(probability) * 100, 2)

        # Step 6: Update usage (MongoDB total_requests or SQLAlchemy usage log)
        if getattr(request, "from_mongo", False):
            increment_total_requests(getattr(request, "_api_key", ""))
        else:
            try:
                usage_log = APIUsageLog(
                    user_id=request.current_user.id,
                    risk_score=risk_score,
                    risk_label=risk_label
                )
                db.session.add(usage_log)
                db.session.commit()
            except Exception as e:
                logger.error("Failed to log usage: %s", e)
                db.session.rollback()

        # Step 7: Format response
        response = {
            "risk_label": risk_label,
            "risk_score": risk_score,
            "status": "High Risk" if prediction == 1 else "Safe"
        }
        
        user_email = getattr(request.current_user, "email", None) or (request.current_user or {}).get("email", "?")
        logger.info("Prediction for user %s - Risk Label: %s, Risk Score: %s%%", user_email, risk_label, risk_score)
        return jsonify(response), 200
    
    except Exception as e:
        db.session.rollback()
        logger.error(f"Unexpected error in /predict endpoint: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500
