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
    
    # Security
    SECRET_KEY: str
    
    # Database (Shared MongoDB)
    MONGODB_URL: str
    MONGODB_DB_NAME: str = "omnipricex"
    
    # gRPC Configuration
    GRPC_PORT: int
    GRPC_MAX_WORKERS: int = 10
    
    # Service Discovery
    CONSUL_HOST: str = "localhost"
    CONSUL_PORT: int = 8500
    HEALTH_CHECK_INTERVAL: int = 30
    
    # Redis (Shared cache/messaging)
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # Metrics
    METRICS_ENABLED: bool = True
    PROMETHEUS_PORT: int = 9090
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Timeouts
    REQUEST_TIMEOUT: int = 30
    DB_TIMEOUT: int = 10
    GRPC_TIMEOUT: int = 30
    
    class Config:
        env_file = ".env"
        case_sensitive = True

class APIGatewaySettings(BaseServiceSettings):
    """API Gateway specific settings"""
    SERVICE_NAME: str = "api-gateway"
    SERVICE_PORT: int = 8000
    GRPC_PORT: int = 50000
    
    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8080"]
    
    # Rate Limiting
    RATE_LIMIT_REQUESTS_PER_MINUTE: int = 100
    RATE_LIMIT_BURST: int = 20
    
    # Service endpoints
    PRODUCT_SERVICE_URL: str = "localhost:50001"
    PRICING_SERVICE_URL: str = "localhost:50002"
    SCRAPER_SERVICE_URL: str = "localhost:50003"
    COMPETITOR_SERVICE_URL: str = "localhost:50004"
    LLM_SERVICE_URL: str = "localhost:50005"

class ProductServiceSettings(BaseServiceSettings):
    """Product Service specific settings"""
    SERVICE_NAME: str = "product-service"
    SERVICE_PORT: int = 8001
    GRPC_PORT: int = 50001

class PricingServiceSettings(BaseServiceSettings):
    """Pricing Service specific settings"""
    SERVICE_NAME: str = "pricing-service"
    SERVICE_PORT: int = 8002
    GRPC_PORT: int = 50002
    
    # ML Model settings
    MODEL_PATH: str = "./models"
    MODEL_RETRAIN_INTERVAL: int = 86400  # 24 hours

class ScraperServiceSettings(BaseServiceSettings):
    """Scraper Service specific settings"""
    SERVICE_NAME: str = "scraper-service"
    SERVICE_PORT: int = 8003
    GRPC_PORT: int = 50003
    
    # Scraping settings
    USER_AGENT: str = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    DELAY_MIN: int = 1
    DELAY_MAX: int = 3
    TIMEOUT: int = 30
    MAX_CONCURRENT_REQUESTS: int = 5
    
    # Celery for async scraping
    CELERY_BROKER_URL: str = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/1"

class CompetitorServiceSettings(BaseServiceSettings):
    """Competitor Service specific settings"""
    SERVICE_NAME: str = "competitor-service"
    SERVICE_PORT: int = 8004
    GRPC_PORT: int = 50004

class LLMServiceSettings(BaseServiceSettings):
    """LLM Assistant Service specific settings"""
    SERVICE_NAME: str = "llm-assistant-service"
    SERVICE_PORT: int = 8005
    GRPC_PORT: int = 50005
    
    # Google Gemini
    GEMINI_API_KEY: str
    GEMINI_MODEL: str = "gemini-pro"
    GEMINI_TEMPERATURE: float = 0.1
    GEMINI_MAX_TOKENS: int = 1000

# Factory function to get appropriate settings
def get_settings(service_name: str):
    """Get settings for a specific service"""
    settings_map = {
        "api-gateway": APIGatewaySettings,
        "product-service": ProductServiceSettings,
        "pricing-service": PricingServiceSettings,
        "scraper-service": ScraperServiceSettings,
        "competitor-service": CompetitorServiceSettings,
        "llm-assistant-service": LLMServiceSettings,
    }
    
    settings_class = settings_map.get(service_name, BaseServiceSettings)
    return settings_class()
