"""
Authentication routes
Registration and login endpoints for API key generation
"""

from flask import Blueprint, request, jsonify
from api.extensions import db, bcrypt
from api.models import User
import re
import logging

logger = logging.getLogger(__name__)

# NOTE:
# These routes are kept for the original SQLAlchemy-based API flow.
# They are now mounted under the /auth prefix so that the main
# /signup and /login routes (MongoDB + UI) are handled by web_routes.py.
auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


def validate_email(email):
    """Validate email format"""
    if not email or not isinstance(email, str):
        return False
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email.strip()))


def validate_json_format():
    """Validate and parse JSON request body"""
    try:
        if request.is_json:
            data = request.json
        else:
            import json
            data = json.loads(request.data.decode('utf-8'))
        
        if not isinstance(data, dict):
            return None, "JSON body must be an object/dictionary", 400
        
        return data, None, None
    except Exception as e:
        logger.error(f"JSON parsing error: {str(e)}")
        return None, "Invalid JSON format in request body", 400


@auth_bp.route("/register", methods=["POST"])
def register():
    """
    Register a new user and generate API key.
    
    Request Body:
    {
        "email": "user@example.com",
        "password": "password123"
    }
    
    Returns:
        201: User created successfully with API key
        400: Invalid input
        409: Email already exists
        500: Internal server error
    """
    try:
        # Validate JSON format
        data, error_msg, status = validate_json_format()
        if data is None:
            return jsonify({"error": error_msg}), status
        
        email = data.get("email")
        password = data.get("password")
        
        # Validate required fields
        if not email:
            return jsonify({"error": "email is required"}), 400
        if not password:
            return jsonify({"error": "password is required"}), 400
        
        # Validate email format
        if not validate_email(email):
            return jsonify({"error": "Invalid email format"}), 400
        
        # Validate password length (minimum 6 characters as per requirements)
        if len(password) < 6:
            return jsonify({"error": "Password must be at least 6 characters"}), 400
        
        # Check if email already exists
        existing_user = User.query.filter_by(email=email.strip().lower()).first()
        if existing_user:
            return jsonify({"error": "An account with this email already exists"}), 409
        
        # Hash password
        password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
        
        # Create new user (API key generated automatically in __init__)
        new_user = User(email=email, password_hash=password_hash)
        
        # Save to database
        db.session.add(new_user)
        db.session.commit()
        
        logger.info(f"New user registered: {email}")
        
        return jsonify({
            "message": "User registered successfully",
            "api_key": new_user.api_key,
            "email": new_user.email
        }), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Registration error: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500


@auth_bp.route("/login", methods=["POST"])
def login():
    """
    Login with email and password, returns API key.
    
    Request Body:
    {
        "email": "user@example.com",
        "password": "password123"
    }
    
    Returns:
        200: Login successful with API key
        400: Invalid input
        401: Invalid credentials
        500: Internal server error
    """
    try:
        # Validate JSON format
        data, error_msg, status = validate_json_format()
        if data is None:
            return jsonify({"error": error_msg}), status
        
        email = data.get("email")
        password = data.get("password")
        
        # Validate required fields
        if not email or not password:
            return jsonify({"error": "email and password are required"}), 400
        
        # Find user by email
        user = User.query.filter_by(email=email.strip().lower()).first()
        
        # Check if user exists and password matches
        if not user or not bcrypt.check_password_hash(user.password_hash, password):
            return jsonify({"error": "Invalid email or password"}), 401
        
        logger.info(f"User logged in: {email}")
        
        return jsonify({
            "message": "Login successful",
            "api_key": user.api_key,
            "email": user.email
        }), 200
        
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500
