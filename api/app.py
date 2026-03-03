"""
AI Security Risk Prediction API
Production-ready Flask application for security risk assessment.
Modular architecture with separate routes, models, and extensions.
"""

from flask import Flask, jsonify, request
from datetime import datetime
import joblib
import os
import sys
import logging

# Add parent directory to path for imports
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from config import get_config
from api.extensions import db, bcrypt, cors
from api.models import User, APIUsageLog
from api.auth_routes import auth_bp
from api.predict_routes import predict_bp, set_model
from api.web_routes import web_bp

# ============================================================================
# CONFIGURATION
# ============================================================================

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create Flask app; templates and static now live alongside app.py
# Flask defaults to 'templates' and 'static' directories relative to this file.
app = Flask(__name__)

# Load configuration
config_class = get_config()
app.config.from_object(config_class)

# Initialize extensions
db.init_app(app)
bcrypt.init_app(app)
cors.init_app(app)

# Register blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(predict_bp)
app.register_blueprint(web_bp)

# ============================================================================
# MODEL LOADING
# ============================================================================

model_path = os.path.join(BASE_DIR, "model", "model.pkl")

ml_model = None
try:
    ml_model = joblib.load(model_path)
    logger.info(f"Model loaded successfully from {model_path}")
    # Set model in predict_routes module
    set_model(ml_model)
except FileNotFoundError:
    logger.error(f"Model file not found at {model_path}")
except Exception as e:
    logger.error(f"Error loading model: {str(e)}")


# ============================================================================
# DATABASE INITIALIZATION
# ============================================================================

def init_db():
    """Initialize database tables"""
    with app.app_context():
        db.create_all()
        logger.info("Database tables initialized")


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
    """Set JSON content type only for API responses (not for HTML pages)"""
    if response.content_type == "text/html; charset=utf-8" or response.content_type.startswith("text/html"):
        return response
    if response.content_type == "application/octet-stream":
        return response
    # Default API responses to JSON when not already set
    if "application/json" not in (response.content_type or ""):
        response.headers["Content-Type"] = "application/json"
    return response


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
        "message": "AI Security API running",
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "model_loaded": ml_model is not None,
        "version": app.config.get('API_VERSION', '1.0.0')
    }), 200


@app.route("/health", methods=["GET"])
def health():
    """Alias for health check endpoint"""
    return health_check()


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
    
    # Initialize database
    init_db()
    
    # Determine port - prefer explicit PORT env var (used by platforms like Railway)
    port = int(os.environ.get('PORT', app.config.get('PORT', 5000)))

    # Run app
    app.run(
        debug=app.config.get('DEBUG', False),
        host=app.config.get('HOST', '127.0.0.1'),
        port=port,
        threaded=app.config.get('THREADED', True)
    )
