import os
from datetime import timedelta

class Config:
    """Base configuration class"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'canteen-secret-key-change-in-production'
    SESSION_PERMANENT = False
    REMEMBER_COOKIE_DURATION = timedelta(minutes=30)
    
    # Database configuration
    if os.environ.get('DATABASE_URL'):
        # Production: Use PostgreSQL
        SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
        # Handle Heroku's postgres:// vs postgresql:// issue
        if SQLALCHEMY_DATABASE_URI.startswith('postgres://'):
            SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI.replace('postgres://', 'postgresql://', 1)
    else:
        # Development: Use local SQLite
        SQLALCHEMY_DATABASE_URI = 'sqlite:///database.db'
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # File upload configuration
    UPLOAD_FOLDER = 'static/uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    
    # Barcode configuration
    BARCODE_FOLDER = 'static/barcodes'

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    
class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    
class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'

# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
