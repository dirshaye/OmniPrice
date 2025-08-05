"""
Scheduler Service Configuration
"""

import os
from pydantic_settings import BaseSettings
from typing import Optional, List

class Settings(BaseSettings):
    # Service settings
    SERVICE_NAME: str = "scheduler-service"
    VERSION: str = "1.0.0"
    DEBUG: bool = False
    GRPC_PORT: int = int(os.getenv("GRPC_PORT", "50054"))  # Port for gRPC server
    
    # Database settings (MongoDB for job metadata)
    MONGODB_URL: str = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
    DATABASE_NAME: str = "scheduler_service_db"
    
    # Celery Configuration
    CELERY_BROKER_URL: str = os.getenv("CELERY_BROKER_URL", "amqp://guest:guest@rabbitmq:5672//")
    CELERY_RESULT_BACKEND: str = os.getenv("CELERY_RESULT_BACKEND", "redis://redis:6379/0")
    CELERY_TASK_SERIALIZER: str = "json"
    CELERY_RESULT_SERIALIZER: str = "json"
    CELERY_ACCEPT_CONTENT: List[str] = ["json"]
    CELERY_TIMEZONE: str = "UTC"
    CELERY_ENABLE_UTC: bool = True
    CELERY_BEAT_SCHEDULE_FILENAME: str = "celerybeat-schedule"
    
    # External service URLs (gRPC endpoints)
    SCRAPER_SERVICE_URL: str = os.getenv("SCRAPER_SERVICE_URL", "localhost:50053")
    PRICING_SERVICE_URL: str = os.getenv("PRICING_SERVICE_URL", "localhost:50052")
    PRODUCT_SERVICE_URL: str = os.getenv("PRODUCT_SERVICE_URL", "localhost:50051")
    
    # Scheduler settings
    TIMEZONE: str = "UTC"
    MAX_CONCURRENT_JOBS: int = 10
    JOB_RETRY_ATTEMPTS: int = 3
    JOB_RETRY_DELAY: int = 60  # seconds
    
    # Default schedules (cron expressions)
    COMPETITOR_SCRAPE_SCHEDULE: str = "0 */6 * * *"  # Every 6 hours
    PRICE_UPDATE_SCHEDULE: str = "0 8 * * *"  # Daily at 8 AM
    HEALTH_CHECK_SCHEDULE: str = "*/5 * * * *"  # Every 5 minutes
    
    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# Global settings instance
settings = Settings()
