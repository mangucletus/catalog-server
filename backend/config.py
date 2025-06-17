import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Configuration class for Flask application"""
    # Database configuration
    # Format: postgresql://username:password@localhost/database_name
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DATABASE_URL', 
        'postgresql://catalog_user:catalog_pass@localhost/catalog'
    )
    
    # Disable SQLAlchemy event system to save resources
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Secret key for session management (change this in production!)
    SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-change-in-production')
    
    # CORS settings - allows frontend to communicate with backend
    CORS_ORIGINS = ["http://localhost:3000", "https://your-domain.com"]