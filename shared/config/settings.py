"""
Shared configuration classes for OmniPriceX microservices.
This replaces individual service config files to maintain consistency.
"""

from pydantic_settings import BaseSettings
from typing import Optional, List
import os
from dotenv import load_dotenv

load_dotenv()

class BaseServiceSettings(BaseSettings):
    """Base settings for all microservices"""
    
    # Service identification
    SERVICE_NAME: str
    SERVICE_VERSION: str = "1.0.0"
    SERVICE_PORT: int
    
    # Environment
    DEBUG: bool = True
    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "INFO"
    
    # Security
    SECRET_KEY: str
    JWT_SECRET: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Database (Shared MongoDB)
    MONGO_URI: str
    MONGO_DB: str = "omnipricex"
    
    # gRPC Configuration
    GRPC_PORT: int
    GRPC_MAX_WORKERS: int = 10
    
    # Redis Configuration
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # External APIs
    GEMINI_API_KEY: Optional[str] = None
    OPENAI_API_KEY: Optional[str] = None
    
    class Config:
        env_file = ".env"
        case_sensitive = True


class APIGatewaySettings(BaseServiceSettings):
    """API Gateway specific settings"""
    SERVICE_NAME: str = "api-gateway"
    SERVICE_PORT: int = 8000
    GRPC_PORT: int = 50000
    
    # Service URLs for gRPC communication
    PRODUCT_SERVICE_URL: str = "localhost:50051"
    PRICING_SERVICE_URL: str = "localhost:50052"
    SCRAPER_SERVICE_URL: str = "localhost:50053"
    COMPETITOR_SERVICE_URL: str = "localhost:50054"
    ANALYTICS_SERVICE_URL: str = "localhost:50055"
    LLM_ASSISTANT_SERVICE_URL: str = "localhost:50056"
    AUTH_SERVICE_URL: str = "localhost:50057"


class ProductServiceSettings(BaseServiceSettings):
    """Product Service specific settings"""
    SERVICE_NAME: str = "product-service"
    SERVICE_PORT: int = 8001
    GRPC_PORT: int = 50051


class PricingServiceSettings(BaseServiceSettings):
    """Pricing Service specific settings"""
    SERVICE_NAME: str = "pricing-service"
    SERVICE_PORT: int = 8002
    GRPC_PORT: int = 50052


class ScraperServiceSettings(BaseServiceSettings):
    """Scraper Service specific settings"""
    SERVICE_NAME: str = "scraper-service"
    SERVICE_PORT: int = 8003
    GRPC_PORT: int = 50053
    
    # Scraping specific settings
    SCRAPE_TIMEOUT: int = 30
    MAX_CONCURRENT_SCRAPES: int = 5
    USER_AGENT: str = "OmniPriceX-Bot/1.0"


class CompetitorServiceSettings(BaseServiceSettings):
    """Competitor Service specific settings"""
    SERVICE_NAME: str = "competitor-service"
    SERVICE_PORT: int = 8004
    GRPC_PORT: int = 50054


class AnalyticsServiceSettings(BaseServiceSettings):
    """Analytics Service specific settings"""
    SERVICE_NAME: str = "analytics-service"
    SERVICE_PORT: int = 8005
    GRPC_PORT: int = 50055


class LLMAssistantServiceSettings(BaseServiceSettings):
    """LLM Assistant Service specific settings"""
    SERVICE_NAME: str = "llm-assistant-service"
    SERVICE_PORT: int = 8006
    GRPC_PORT: int = 50056


class AuthServiceSettings(BaseServiceSettings):
    """Auth Service specific settings"""
    SERVICE_NAME: str = "auth-service"
    SERVICE_PORT: int = 8007
    GRPC_PORT: int = 50057
    
    # Auth specific settings
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    PASSWORD_MIN_LENGTH: int = 8
