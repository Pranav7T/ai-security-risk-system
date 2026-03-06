"""
Configuration settings for AI Security Risk Detection API
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """Base configuration"""
    
    # Flask Settings
    DEBUG = False
    TESTING = False
    JSON_SORT_KEYS = False
    
    # API Settings
    API_VERSION = os.getenv('API_VERSION', '1.0.0')
    API_NAME = os.getenv('API_NAME', 'AI Security Risk Detection API')
    
    # Server Settings
    HOST = os.getenv('FLASK_HOST', '127.0.0.1')
    PORT = int(os.getenv('FLASK_PORT', 5000))
    THREADED = True
    
    # Model Settings
    MODEL_PATH = os.getenv('MODEL_PATH', 'model/model.pkl')

    # Database (SQLite for Level 1)
    DATABASE_PATH = os.getenv('DATABASE_PATH', os.path.join(os.path.dirname(os.path.abspath(__file__)), 'instance', 'app.db'))
    
    # SQLAlchemy Configuration
    SQLALCHEMY_DATABASE_URI = os.getenv('SQLALCHEMY_DATABASE_URI', f'sqlite:///{DATABASE_PATH}')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False
    
    # MongoDB (for signup/login/dashboard and usage)
    # default uses Atlas connection with encoded password (replace with your own or set via .env)
    MONGODB_URI = os.getenv(
        'MONGODB_URI',
        'mongodb+srv://sononipranav_db_user:%40Sononi5684@cluster0.36nxwba.mongodb.net/?retryWrites=true&w=majority'
    )
    MONGODB_DB = os.getenv('MONGODB_DB', 'ai_security')

    # Logging Settings
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = os.getenv('LOG_FILE', 'api.log')


class DevelopmentConfig(Config):
    """Development configuration"""
    
    DEBUG = True
    TESTING = False
    LOG_LEVEL = 'DEBUG'


class ProductionConfig(Config):
    """Production configuration"""
    
    DEBUG = False
    TESTING = False
    LOG_LEVEL = 'INFO'
    
    # Static file configuration for Railway
    STATIC_FOLDER = 'api/static'
    TEMPLATES_FOLDER = 'api/templates'


class TestingConfig(Config):
    """Testing configuration"""
    
    TESTING = True
    DEBUG = True
    LOG_LEVEL = 'DEBUG'


# Configuration selector
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}


def get_config(env=None):
    """
    Get configuration based on environment
    
    Args:
        env (str): Environment name (development, production, testing)
    
    Returns:
        Config: Configuration class for the specified environment
    """
    if env is None:
        env = os.getenv('FLASK_ENV', 'development')
    
    return config.get(env, config['default'])
