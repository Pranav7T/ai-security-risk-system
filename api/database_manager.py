"""
Database manager that handles MongoDB and SQLite fallback.
Provides a unified interface for database operations.
"""

import logging
import os
from api.mongodb import test_connection as mongodb_test, insert_user as mongodb_insert_user, find_user_by_email as mongodb_find_user_by_email, find_user_by_api_key as mongodb_find_user_by_api_key, increment_total_requests as mongodb_increment_requests

try:
    from api.sqlite_fallback import test_connection as sqlite_test, insert_user as sqlite_insert_user, find_user_by_email as sqlite_find_user_by_email, find_user_by_api_key as sqlite_find_user_by_api_key, increment_total_requests as sqlite_increment_requests, init_db
    SQLITE_AVAILABLE = True
except ImportError:
    SQLITE_AVAILABLE = False

# Import Railway configuration if available
try:
    from api.railway_config import setup_railway_environment, get_railway_database_config
    RAILWAY_AVAILABLE = True
except ImportError:
    RAILWAY_AVAILABLE = False

logger = logging.getLogger(__name__)

# Initialize Railway environment if available
if RAILWAY_AVAILABLE:
    setup_railway_environment()

# Determine which backend to use
def initialize_backend():
    """Initialize the appropriate database backend."""
    
    # Check for Railway-specific configuration first
    if RAILWAY_AVAILABLE:
        railway_config = get_railway_database_config()
        if railway_config['backend'] == 'sqlite':
            if SQLITE_AVAILABLE and sqlite_test():
                logger.info(f"Railway: Using SQLite ({railway_config['reason']})")
                return 'sqlite'
    
    # Standard fallback logic
    if mongodb_test():
        logger.info("Using MongoDB as primary database")
        return "mongodb"
    elif SQLITE_AVAILABLE and sqlite_test():
        logger.info("Using SQLite as fallback database")
        return "sqlite"
    else:
        logger.error("No database backend available!")
        return "none"

BACKEND = initialize_backend()

def test_connection():
    """Test database connection."""
    if BACKEND == "mongodb":
        return mongodb_test()
    elif BACKEND == "sqlite":
        return sqlite_test()
    else:
        return False

def insert_user(name, email, password_hash, api_key):
    """Insert a new user."""
    if BACKEND == "mongodb":
        return mongodb_insert_user(name, email, password_hash, api_key)
    elif BACKEND == "sqlite":
        return sqlite_insert_user(name, email, password_hash, api_key)
    else:
        logger.error("No database backend available for insert_user")
        return False

def find_user_by_email(email):
    """Find user by email."""
    if BACKEND == "mongodb":
        return mongodb_find_user_by_email(email)
    elif BACKEND == "sqlite":
        return sqlite_find_user_by_email(email)
    else:
        logger.error("No database backend available for find_user_by_email")
        return None

def find_user_by_api_key(api_key):
    """Find user by API key."""
    if BACKEND == "mongodb":
        return mongodb_find_user_by_api_key(api_key)
    elif BACKEND == "sqlite":
        return sqlite_find_user_by_api_key(api_key)
    else:
        logger.error("No database backend available for find_user_by_api_key")
        return None

def increment_total_requests(api_key):
    """Increment total requests for user."""
    if BACKEND == "mongodb":
        return mongodb_increment_requests(api_key)
    elif BACKEND == "sqlite":
        return sqlite_increment_requests(api_key)
    else:
        logger.error("No database backend available for increment_total_requests")
        return False

def get_backend_info():
    """Get information about the current database backend."""
    return {
        "backend": BACKEND,
        "available": BACKEND != "none",
        "mongodb_available": mongodb_test(),
        "sqlite_available": SQLITE_AVAILABLE and (sqlite_test() if SQLITE_AVAILABLE else False)
    }
