"""
Core Configuration Module for OmniPrice

Technical Explanation:
- Uses Pydantic Settings to load environment variables from .env file
- BaseSettings automatically validates types and required fields
- We define all configuration in one place for consistency
- Each setting has a default value for development
"""

from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables
    
    Technical Note:
    - Pydantic will automatically convert env var types (str -> int, str -> bool, etc.)
    - Variables are read from .env file if it exists
    - You can override settings by setting environment variables
    """
    
    # Application Settings
    APP_NAME: str = "OmniPrice"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    ENVIRONMENT: str = "development"  # development, staging, production
    
    # API Settings
    API_V1_PREFIX: str = "/api/v1"
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # MongoDB Database Configuration
    # Technical Note: MongoDB connection string format
    # mongodb://username:password@host:port/database_name
    MONGODB_URL: str = "mongodb://admin:password@localhost:27017"
    MONGODB_DB_NAME: str = "omniprice"
    
    # Redis Cache Configuration  
    # Technical Note: Redis is an in-memory key-value store for caching
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: Optional[str] = None
    
    # JWT Security Settings
    # Technical Note: JWT (JSON Web Tokens) for stateless authentication
    SECRET_KEY: str = "your-secret-key-change-in-production"  # MUST change in .env
    ALGORITHM: str = "HS256"  # HMAC with SHA-256
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # CORS Settings
    # Technical Note: CORS allows frontend (different domain) to call our API
    CORS_ORIGINS: list = [
        "http://localhost:3000",  # React development server
        "http://localhost:8000",  # API itself
    ]
    
    # External API Keys
    GEMINI_API_KEY: Optional[str] = None  # Google Gemini AI
    OPENAI_API_KEY: Optional[str] = None  # OpenAI GPT
    
    # Scraper Settings
    SCRAPER_USER_AGENT: str = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    SCRAPER_TIMEOUT: int = 10  # seconds
    SCRAPER_MAX_RETRIES: int = 3
    
    # Logging
    LOG_LEVEL: str = "INFO"  # DEBUG, INFO, WARNING, ERROR, CRITICAL
    
    class Config:
        """
        Pydantic configuration
        
        Technical Note:
        - env_file tells Pydantic to load from .env file
        - case_sensitive=False means MONGODB_URL and mongodb_url are the same
        """
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"


# Singleton instance
# Technical Note: We create one global settings instance
# This is loaded once when the app starts and reused everywhere
settings = Settings()


# Helper function to get settings
def get_settings() -> Settings:
    """
    Dependency injection helper for FastAPI
    
    Usage in FastAPI route:
    @router.get("/")
    async def read_root(settings: Settings = Depends(get_settings)):
        return {"app_name": settings.APP_NAME}
    """
    return settings
