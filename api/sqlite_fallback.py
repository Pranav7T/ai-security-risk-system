"""
SQLite fallback for when MongoDB is not available.
This provides the same interface as mongodb.py but uses SQLite.
"""

import sqlite3
import logging
import uuid
import hashlib
from contextlib import contextmanager
from api.extensions import bcrypt

logger = logging.getLogger(__name__)

DB_PATH = "instance/ai_security.db"

def get_db_connection():
    """Get SQLite database connection."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

@contextmanager
def get_db():
    """Context manager for database operations."""
    conn = get_db_connection()
    try:
        yield conn
        conn.commit()
    except Exception as e:
        conn.rollback()
        logger.error("SQLite operation failed: %s", e)
        raise
    finally:
        conn.close()

def init_db():
    """Initialize SQLite database with users table."""
    import os
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    
    with get_db() as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                api_key TEXT UNIQUE NOT NULL,
                total_requests INTEGER DEFAULT 0
            )
        ''')

def test_connection():
    """Test SQLite connection."""
    try:
        init_db()
        with get_db() as conn:
            conn.execute("SELECT 1")
        logger.info("SQLite connection successful")
        return True
    except Exception as e:
        logger.error("SQLite connection failed: %s", e)
        return False

def find_user_by_email(email):
    """Find user by email."""
    if not email or not str(email).strip():
        return None
    try:
        with get_db() as conn:
            cursor = conn.execute(
                "SELECT * FROM users WHERE email = ?",
                (str(email).strip().lower(),)
            )
            row = cursor.fetchone()
            return dict(row) if row else None
    except Exception as e:
        logger.error("SQLite find_user_by_email: %s", e)
        return None

def find_user_by_api_key(api_key):
    """Find user by API key (excluding password)."""
    if not api_key or not str(api_key).strip():
        return None
    try:
        with get_db() as conn:
            cursor = conn.execute(
                "SELECT id, name, email, api_key, total_requests FROM users WHERE api_key = ?",
                (api_key.strip(),)
            )
            row = cursor.fetchone()
            if row:
                user = dict(row)
                user["id"] = str(user["id"])
                return user
            return None
    except Exception as e:
        logger.error("SQLite find_user_by_api_key: %s", e)
        return None

def insert_user(name, email, password_hash, api_key):
    """Insert a new user."""
    try:
        with get_db() as conn:
            conn.execute(
                "INSERT INTO users (name, email, password, api_key, total_requests) VALUES (?, ?, ?, ?, 0)",
                (name, email, password_hash, api_key)
            )
        return True
    except Exception as e:
        logger.error("SQLite insert_user: %s", e)
        return False

def increment_total_requests(api_key):
    """Increment total_requests for user."""
    if not api_key or not str(api_key).strip():
        return False
    try:
        with get_db() as conn:
            cursor = conn.execute(
                "UPDATE users SET total_requests = total_requests + 1 WHERE api_key = ?",
                (api_key.strip(),)
            )
            return cursor.rowcount == 1
    except Exception as e:
        logger.error("SQLite increment_total_requests: %s", e)
        return False
