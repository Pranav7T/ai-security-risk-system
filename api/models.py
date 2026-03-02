"""
SQLAlchemy database models
User and APIUsageLog models for the AI Security API platform
"""

from datetime import datetime
from api.extensions import db
import secrets


class User(db.Model):
    """User model for authentication and API key management"""
    
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    api_key = db.Column(db.String(64), unique=True, nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationship to usage logs
    usage_logs = db.relationship('APIUsageLog', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    
    def __init__(self, email, password_hash, api_key=None):
        """Initialize user with email and password hash. Generate API key if not provided."""
        self.email = email.strip().lower()
        self.password_hash = password_hash
        self.api_key = api_key or self._generate_api_key()
    
    @staticmethod
    def _generate_api_key():
        """Generate a secure 64-character hex API key"""
        return secrets.token_hex(32)
    
    def to_dict(self):
        """Convert user to dictionary (excludes password_hash)"""
        return {
            'id': self.id,
            'email': self.email,
            'api_key': self.api_key,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f'<User {self.email}>'


class APIUsageLog(db.Model):
    """API usage logging model - tracks each prediction request"""
    
    __tablename__ = 'api_usage_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    risk_score = db.Column(db.Float, nullable=False)
    risk_label = db.Column(db.Integer, nullable=False)
    
    def __init__(self, user_id, risk_score, risk_label):
        """Initialize usage log entry"""
        self.user_id = user_id
        self.risk_score = risk_score
        self.risk_label = risk_label
    
    def to_dict(self):
        """Convert usage log to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'risk_score': self.risk_score,
            'risk_label': self.risk_label
        }
    
    def __repr__(self):
        return f'<APIUsageLog user_id={self.user_id} risk_score={self.risk_score}>'
