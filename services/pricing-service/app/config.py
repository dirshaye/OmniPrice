"""
Pricing Service Configuration
"""

import os
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Service settings
    SERVICE_NAME: str = "pricing-service"
    VERSION: str = "1.0.0"
    DEBUG: bool = False
    PORT: int = int(os.getenv("PORT", "8002"))
    GRPC_PORT: int = int(os.getenv("GRPC_PORT", "50052"))
    
    # Database settings - Use same MongoDB instance but different database
    MONGO_URI: str = os.getenv("MONGO_URI", "mongodb://localhost:27017")
    MONGO_DB: str = "pricing_service_db"  # Different DB name for isolation
    
    # External service URLs (for microservice communication)
    PRODUCT_SERVICE_URL: str = os.getenv("PRODUCT_SERVICE_URL", "localhost:50053")
    LLM_ASSISTANT_URL: str = os.getenv("LLM_ASSISTANT_URL", "localhost:8002")
    
    # Pricing engine settings
    DEFAULT_CONFIDENCE_THRESHOLD: float = 0.7
    MAX_PRICE_CHANGE_PERCENTAGE: float = 20.0  # Maximum price change allowed
    MIN_PRICE_THRESHOLD: float = 0.01  # Minimum price in USD
    
    # Business rules
    COMPETITOR_PRICE_WEIGHT: float = 0.4
    MARKET_DEMAND_WEIGHT: float = 0.3
    COST_MARGIN_WEIGHT: float = 0.3
    
    # Cache settings
    CACHE_TTL_SECONDS: int = 300  # 5 minutes
    
    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# Global settings instance
settings = Settings()