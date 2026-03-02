"""
Web routes: signup, login, dashboard pages and API endpoints using MongoDB.
College-level simple: name, email, password, api_key (UUID), total_requests.
"""

import re
import uuid
import logging
from flask import Blueprint, request, jsonify, render_template

from api.extensions import bcrypt
from api.mongodb import (
    get_users_collection,
    find_user_by_email,
    find_user_by_api_key,
)

logger = logging.getLogger(__name__)

web_bp = Blueprint("web", __name__)


def _validate_email(email):
    if not email or not isinstance(email, str):
        return False
    return bool(re.match(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", email.strip()))


def _get_json():
    try:
        if request.is_json:
            return request.get_json(), None
        import json
        return json.loads(request.data.decode("utf-8")), None
    except Exception as e:
        logger.warning("JSON parse error: %s", e)
        return None, "Invalid JSON"


# ----- Page routes (serve HTML) -----


@web_bp.route("/home", methods=["GET"])
def landing_page():
    return render_template("landing.html")


@web_bp.route("/signup", methods=["GET"])
def signup_page():
    return render_template("signup.html")


@web_bp.route("/login", methods=["GET"])
def login_page():
    return render_template("login.html")


@web_bp.route("/dashboard", methods=["GET"])
def dashboard_page():
    return render_template("dashboard.html")


# ----- API routes (JSON) -----


@web_bp.route("/signup", methods=["POST"])
def signup():
    """
    POST /signup
    Body: { "name": "", "email": "", "password": "" }
    Returns: { "message": "User created successfully", "api_key": "..." }
    """
    data, err = _get_json()
    if data is None:
        return jsonify({"error": err or "Invalid JSON"}), 400

    name = (data.get("name") or "").strip()
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    if not name:
        return jsonify({"error": "Name is required"}), 400
    if not email:
        return jsonify({"error": "Email is required"}), 400
    if not password:
        return jsonify({"error": "Password is required"}), 400
    if not _validate_email(email):
        return jsonify({"error": "Invalid email format"}), 400
    if len(password) < 6:
        return jsonify({"error": "Password must be at least 6 characters"}), 400

    if find_user_by_email(email):
        return jsonify({"error": "Email already registered"}), 400

    api_key = str(uuid.uuid4())
    password_hash = bcrypt.generate_password_hash(password).decode("utf-8")

    try:
        get_users_collection().insert_one({
            "name": name,
            "email": email,
            "password": password_hash,
            "api_key": api_key,
            "total_requests": 0,
        })
    except Exception as e:
        logger.error("MongoDB insert on signup: %s", e)
        return jsonify({"error": "Internal server error"}), 500

    logger.info("User signed up: %s", email)
    return jsonify({
        "message": "User created successfully",
        "api_key": api_key,
        "email": email,
    }), 200


@web_bp.route("/login", methods=["POST"])
def login():
    """
    POST /login
    Body: { "email": "", "password": "" }
    Returns: { "message": "Login successful", "api_key": "..." }
    """
    data, err = _get_json()
    if data is None:
        return jsonify({"error": err or "Invalid JSON"}), 400

    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400

    user = find_user_by_email(email)
    if not user:
        return jsonify({"error": "Invalid email or password"}), 401

    stored = user.get("password") or ""
    if not bcrypt.check_password_hash(stored, password):
        return jsonify({"error": "Invalid email or password"}), 401

    logger.info("User logged in: %s", email)
    return jsonify({
        "message": "Login successful",
        "api_key": user["api_key"],
        "email": user["email"],
    }), 200


@web_bp.route("/dashboard-data", methods=["GET"])
def dashboard_data():
    """
    GET /dashboard-data
    Header: x-api-key
    Returns: { "name", "email", "api_key", "total_requests" }
    """
    api_key = request.headers.get("x-api-key")
    if not api_key:
        return jsonify({"error": "API key required"}), 401

    user = find_user_by_api_key(api_key)
    if not user:
        return jsonify({"error": "Invalid or expired API key"}), 401

    return jsonify({
        "name": user.get("name", ""),
        "email": user.get("email", ""),
        "api_key": user.get("api_key", ""),
        "total_requests": user.get("total_requests", 0),
    }), 200
