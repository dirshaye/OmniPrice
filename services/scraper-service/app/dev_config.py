"""
Development configuration with local services
"""

from .config import Settings

class DevSettings(Settings):
    """Development settings"""
    
    DEBUG: bool = True
    LOG_LEVEL: str = "DEBUG"
    
    # Local MongoDB
    MONGODB_URL: str = "mongodb://localhost:27017"
    
    # Local Redis for Celery
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/0"
    
    # Development browser settings
    HEADLESS_BROWSER: bool = False  # Show browser for debugging
