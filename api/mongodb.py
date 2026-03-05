"""
MongoDB connection and helpers for AI Security API.
Users collection: name, email, password (hashed), api_key, total_requests
"""

import os
import logging
from pymongo import MongoClient
from pymongo.errors import PyMongoError
from pymongo.server_api import ServerApi

logger = logging.getLogger(__name__)

# Default MongoDB Atlas URI with credentials provided by user.
# The password contains an '@' so it must be URL-encoded as '%40'.
# You can override via the MONGODB_URI environment variable.
DEFAULT_ATLAS_URI = (
    "mongodb+srv://sononipranav_db_user:%40Sononi5684@"
    "cluster0.36nxwba.mongodb.net/?retryWrites=true&w=majority"
)
DEFAULT_URI = os.getenv("MONGODB_URI", DEFAULT_ATLAS_URI)
DB_NAME = os.getenv("MONGODB_DB", "ai_security")
USERS_COLLECTION_NAME = "users"

def test_connection():
    """Test MongoDB connection and return status."""
    try:
        client = get_client()
        # Ping the database to test connection
        client.admin.command('ping')
        logger.info("MongoDB connection successful")
        return True
    except Exception as e:
        logger.error("MongoDB connection failed: %s", e)
        return False

_client = None
_db = None
_users_collection = None


def get_client():
    """Get or create MongoDB client.

    Uses ServerApi v1 with strict mode enabled so that the driver
    behaves in a stable, forward-compatible way (similar to the
    Node.js example with ServerApiVersion).
    """
    global _client
    if _client is None:
        # configure stable API with strict/deprecation options
        api = ServerApi('1', strict=True, deprecation_errors=True)
        _client = MongoClient(
            DEFAULT_URI,
            server_api=api,
        )
        logger.info("MongoDB client connected to %s", DEFAULT_URI)
    return _client


def get_db():
    """Get database."""
    global _db
    if _db is None:
        _db = get_client()[DB_NAME]
    return _db


def get_users_collection():
    """Get users collection."""
    global _users_collection
    if _users_collection is None:
        _users_collection = get_db()[USERS_COLLECTION_NAME]
        # Simple index for api_key lookups
        try:
            _users_collection.create_index("api_key", unique=True)
            _users_collection.create_index("email", unique=True)
        except PyMongoError as e:
            logger.warning("Index creation (may already exist): %s", e)
    return _users_collection


def find_user_by_api_key(api_key):
    """
    Return user document (dict) from MongoDB by api_key, or None.
    Excludes password from result for safety.
    """
    if not api_key or not str(api_key).strip():
        return None
    try:
        user = get_users_collection().find_one(
            {"api_key": api_key.strip()},
            {"password": 0}  # never return password
        )
        if user and "_id" in user:
            user["id"] = str(user["_id"])
        return user
    except PyMongoError as e:
        logger.error("MongoDB find_user_by_api_key: %s", e)
        return None


def find_user_by_email(email):
    """Return full user document by email (includes password for login check)."""
    if not email or not str(email).strip():
        return None
    try:
        return get_users_collection().find_one({"email": str(email).strip().lower()})
    except PyMongoError as e:
        logger.error("MongoDB find_user_by_email: %s", e)
        return None


def increment_total_requests(api_key):
    """Increment total_requests for user with given api_key. Returns True if updated."""
    if not api_key or not str(api_key).strip():
        return False
    try:
        r = get_users_collection().update_one(
            {"api_key": api_key.strip()},
            {"$inc": {"total_requests": 1}}
        )
        return r.modified_count == 1
    except PyMongoError as e:
        logger.error("MongoDB increment_total_requests: %s", e)
        return False


def insert_user(name, email, password_hash, api_key):
    """Insert a new user into the database. Returns True if successful."""
    try:
        get_users_collection().insert_one({
            "name": name,
            "email": email,
            "password": password_hash,
            "api_key": api_key,
            "total_requests": 0,
        })
        return True
    except PyMongoError as e:
        logger.error("MongoDB insert_user: %s", e)
        return False


def get_database_backend():
    """Get the appropriate database backend (MongoDB or SQLite fallback)."""
    if test_connection():
        logger.info("Using MongoDB as database backend")
        return "mongodb"
    else:
        logger.warning("MongoDB unavailable, falling back to SQLite")
        try:
            from api.sqlite_fallback import init_db
            init_db()
            return "sqlite"
        except ImportError:
            logger.error("SQLite fallback not available")
            return "none"
