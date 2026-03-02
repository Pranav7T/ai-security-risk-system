"""
MongoDB connection and helpers for AI Security API.
Users collection: name, email, password (hashed), api_key, total_requests
"""

import os
import logging
from pymongo import MongoClient
from pymongo.errors import PyMongoError

logger = logging.getLogger(__name__)

# Default MongoDB URI (local)
DEFAULT_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017/")
DB_NAME = os.getenv("MONGODB_DB", "ai_security")
USERS_COLLECTION_NAME = "users"

_client = None
_db = None
_users_collection = None


def get_client():
    """Get or create MongoDB client."""
    global _client
    if _client is None:
        _client = MongoClient(DEFAULT_URI)
        logger.info("MongoDB client connected")
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
