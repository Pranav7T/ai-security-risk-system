"""
Railway-specific configuration for database handling.
Ensures SQLite works properly in Railway's ephemeral environment.
"""

import os
import logging

logger = logging.getLogger(__name__)

def setup_railway_environment():
    """Setup environment variables for Railway deployment."""
    
    # Railway provides PORT environment variable
    if 'PORT' in os.environ:
        os.environ['FLASK_PORT'] = os.environ['PORT']
    
    # Ensure instance directory exists
    instance_dir = os.path.join(os.getcwd(), 'instance')
    os.makedirs(instance_dir, exist_ok=True)
    
    # Set SQLite database path for Railway
    sqlite_path = os.path.join(instance_dir, 'ai_security.db')
    os.environ['SQLITE_DB_PATH'] = sqlite_path
    
    logger.info(f"Railway environment setup complete. SQLite DB: {sqlite_path}")
    
    return True

def get_railway_database_config():
    """Get database configuration optimized for Railway."""
    
    # Prefer SQLite on Railway for reliability
    railway_env = os.getenv('RAILWAY_ENVIRONMENT', 'production')
    
    if railway_env == 'production':
        # In production on Railway, default to SQLite unless MongoDB is explicitly configured
        mongodb_uri = os.getenv('MONGODB_URI')
        if not mongodb_uri or 'your_username' in mongodb_uri:
            logger.info("Railway: Using SQLite as default database")
            return {
                'backend': 'sqlite',
                'reason': 'railway_production_default'
            }
    
    return {
        'backend': 'auto',
        'reason': 'fallback_to_mongodb'
    }
