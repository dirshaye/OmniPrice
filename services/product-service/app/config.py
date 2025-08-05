#!/usr/bin/env python3
"""
Configuration for Product Service
"""

import os
from typing import Optional
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """Product Service configuration"""
    
    # Service info
    SERVICE_NAME: str = "product-service"
    SERVICE_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # Server configuration
    HOST: str = "0.0.0.0"
    PORT: int = 8003
    GRPC_PORT: int = 50053
    
    # Database configuration
    MONGO_URI: str = os.getenv("MONGO_URI", "mongodb://localhost:27017/omnipricex")
    MONGO_DB: str = "omnipricex"
    
    # Redis configuration (for caching)
    REDIS_URL: str = "redis://localhost:6379"
    CACHE_TTL: int = 3600  # 1 hour
    
    # Business rules
    DEFAULT_CURRENCY: str = "USD"
    DEFAULT_LOW_STOCK_THRESHOLD: int = 10
    MAX_COMPETITORS_PER_PRODUCT: int = 20
    PRICE_HISTORY_LIMIT: int = 100
    
    # Pagination defaults
    DEFAULT_PAGE_SIZE: int = 20
    MAX_PAGE_SIZE: int = 100
    
    # Search configuration
    SEARCH_INDEX_NAME: str = "products_search"
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# Global settings instance
settings = Settings()

# Validation
def validate_settings():
    """Validate critical settings"""
    if not settings.MONGO_URI:
        raise ValueError("MONGO_URI is required")
    
    if not settings.MONGO_DB:
        raise ValueError("MONGO_DB is required")
    
    if settings.GRPC_PORT == settings.PORT:
        raise ValueError("GRPC_PORT and PORT cannot be the same")

# Run validation on import
validate_settings()
