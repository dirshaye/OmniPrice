from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    """Application settings"""
    
    # Service Info
    PROJECT_NAME: str = "OmniPriceX API Gateway"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "Main API Gateway for OmniPriceX platform"
    
    # API Configuration
    API_V1_STR: str = "/api/v1"
    
    # Environment
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    
    # CORS
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:3000",  # React frontend
        "http://localhost:8000",  # API Gateway
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8000",
    ]
    
    # Service Hosts
    PRODUCT_SERVICE_HOST: str = os.getenv("PRODUCT_SERVICE_HOST", "product-service")
    PRODUCT_SERVICE_PORT: int = int(os.getenv("PRODUCT_SERVICE_PORT", "50051"))
    
    PRICING_SERVICE_HOST: str = os.getenv("PRICING_SERVICE_HOST", "pricing-service")
    PRICING_SERVICE_PORT: int = int(os.getenv("PRICING_SERVICE_PORT", "50052"))
    
    AUTH_SERVICE_HOST: str = os.getenv("AUTH_SERVICE_HOST", "auth-service")
    AUTH_SERVICE_PORT: int = int(os.getenv("AUTH_SERVICE_PORT", "8001"))
    
    SCHEDULER_SERVICE_HOST: str = os.getenv("SCHEDULER_SERVICE_HOST", "scheduler-service")
    SCHEDULER_SERVICE_PORT: int = int(os.getenv("SCHEDULER_SERVICE_PORT", "50054"))
    
    LLM_ASSISTANT_SERVICE_HOST: str = os.getenv("LLM_ASSISTANT_SERVICE_HOST", "llm-assistant-service")
    LLM_ASSISTANT_SERVICE_PORT: int = int(os.getenv("LLM_ASSISTANT_SERVICE_PORT", "50053"))
    
    # Authentication
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    class Config:
        env_file = ".env"
        case_sensitive = True


def get_settings() -> Settings:
    """Get application settings"""
    return Settings()
