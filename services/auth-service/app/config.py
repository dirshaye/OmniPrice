from functools import lru_cache
from pydantic_settings import BaseSettings
from pydantic import ConfigDict
from typing import Optional

class Settings(BaseSettings):
    """
    Application settings and configuration
    """
    model_config = ConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra='ignore'
    )
    
    # Database
    MONGODB_URL: str = "mongodb://localhost:27017"
    DATABASE_NAME: str = "omnipricex_auth"
    
    # JWT Settings
    SECRET_KEY: str = "your-super-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # API Settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "OmniPriceX Auth Service"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "Authentication and authorization service for OmniPriceX platform"
    
    # CORS Settings
    BACKEND_CORS_ORIGINS: list = ["http://localhost:3000", "http://localhost:8080"]
    
    # Redis (for caching and rate limiting)
    REDIS_URL: str = "redis://localhost:6379"
    
    # Environment
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    
    # Email Settings (for notifications)
    SMTP_HOST: Optional[str] = None
    SMTP_PORT: int = 587
    SMTP_USERNAME: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    SMTP_USE_TLS: bool = True
    
    # Security
    BCRYPT_ROUNDS: int = 12
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60

@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings instance
    """
    return Settings()

# Create global settings instance
settings = get_settings()
