"""
Configuration for scraper service
"""

from functools import lru_cache
from pydantic_settings import BaseSettings
import os

class Settings(BaseSettings):
    """Settings for scraper service"""
    
    # Service configuration
    SERVICE_NAME: str = "scraper-service"
    SERVICE_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # Server configuration
    HOST: str = "0.0.0.0"
    PORT: int = 8004
    GRPC_PORT: int = 50004
    
    # Database configuration
    MONGODB_URL: str = "mongodb://localhost:27017"
    DATABASE_NAME: str = "omnipricex"
    
    # Celery configuration
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/0"
    
    # RabbitMQ (alternative to Redis)
    RABBITMQ_URL: str = "amqp://guest@localhost:5672//"
    
    # Scraping configuration
    SCRAPING_DELAY: float = 1.0  # Delay between requests in seconds
    MAX_CONCURRENT_SCRAPES: int = 5
    SCRAPING_TIMEOUT: int = 30  # Timeout for individual scrape operations
    
    # Browser configuration
    HEADLESS_BROWSER: bool = True
    BROWSER_VIEWPORT_WIDTH: int = 1920
    BROWSER_VIEWPORT_HEIGHT: int = 1080
    
    # Rate limiting
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_PERIOD: int = 3600  # 1 hour
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Health check
    HEALTH_CHECK_INTERVAL: int = 30
    
    # Monitoring
    ENABLE_METRICS: bool = True
    METRICS_PORT: int = 9004
    
    class Config:
        env_file = ".env"
        case_sensitive = True

@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()

# Global settings instance
settings = get_settings()
