"""
Flask extensions initialization
Centralized extension setup for clean imports
"""

from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_cors import CORS

# Initialize extensions (will be initialized in app.py with app context)
db = SQLAlchemy()
bcrypt = Bcrypt()
cors = CORS()
