from pydantic_settings import BaseSettings
from typing import Optional, List
import os
from dotenv import load_dotenv

load_dotenv()

class BaseServiceSettings(BaseSettings):
    """Base settings for all OmniPrice microservices"""
    
    # Service identification
    SERVICE_NAME: str
    SERVICE_VERSION: str = "1.0.0"
    SERVICE_PORT: int
    
    # Environment
    DEBUG: bool = True
    ENVIRONMENT: str = "development"
    
    # Security
    SECRET_KEY: str
    
    # Database (MongoDB Atlas)
    MONGODB_URL: str
    MONGODB_DB_NAME: str = "omniprice"
    
    # gRPC Configuration
    GRPC_PORT: int
    GRPC_MAX_WORKERS: int = 10
    
    # Redis Configuration
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_PASSWORD: Optional[str] = None
    
    # RabbitMQ Configuration (for Celery)
    RABBITMQ_URL: str = "amqp://guest:guest@localhost:5672/"
    
    # Celery Configuration
    CELERY_BROKER_URL: str = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/1"
    
    # External API Keys
    GEMINI_API_KEY: Optional[str] = None
    OPENAI_API_KEY: Optional[str] = None
    SHOPIFY_API_KEY: Optional[str] = None
    SHOPIFY_API_SECRET: Optional[str] = None
    AWS_ACCESS_KEY_ID: Optional[str] = None
    AWS_SECRET_ACCESS_KEY: Optional[str] = None
    GOOGLE_API_KEY: Optional[str] = None
    
    # Auth0 Configuration
    AUTH0_DOMAIN: Optional[str] = None
    AUTH0_API_AUDIENCE: Optional[str] = None
    AUTH0_ISSUER: Optional[str] = None
    AUTH0_ALGORITHMS: List[str] = ["RS256"]
    
    # Prefect Configuration
    PREFECT_API_URL: str = "http://localhost:4200/api"
    PREFECT_ORION_UI_URL: str = "http://localhost:4200"
    
    # Monitoring & Observability
    PROMETHEUS_PORT: int = 9090
    GRAFANA_PORT: int = 3001
    ENABLE_METRICS: bool = True
    LOG_LEVEL: str = "INFO"
    
    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_REQUESTS_PER_MINUTE: int = 60
    
    # Data Pipeline Settings
    MAX_BATCH_SIZE: int = 1000
    DATA_RETENTION_DAYS: int = 365
    ENABLE_DATA_VALIDATION: bool = True
    
    # Scraping Settings
    SCRAPING_DELAY_MS: int = 1000
    MAX_CONCURRENT_REQUESTS: int = 10
    ENABLE_PLAYWRIGHT: bool = True
    USER_AGENT: str = "OmniPrice-Bot/1.0"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# Service-specific configurations
class APIGatewaySettings(BaseServiceSettings):
    SERVICE_NAME: str = "api-gateway"
    SERVICE_PORT: int = 8000
    GRPC_PORT: int = 50050
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "https://omniprice.com"]
    ENABLE_DOCS: bool = True

class ProductServiceSettings(BaseServiceSettings):
    SERVICE_NAME: str = "product-service"
    SERVICE_PORT: int = 8001
    GRPC_PORT: int = 50051

class PricingServiceSettings(BaseServiceSettings):
    SERVICE_NAME: str = "pricing-service"
    SERVICE_PORT: int = 8002
    GRPC_PORT: int = 50052
    
    # Pricing-specific settings
    DEFAULT_MARGIN_PERCENT: float = 25.0
    MIN_MARGIN_PERCENT: float = 5.0
    MAX_MARGIN_PERCENT: float = 100.0
    PRICING_UPDATE_FREQUENCY_HOURS: int = 6

class ScraperServiceSettings(BaseServiceSettings):
    SERVICE_NAME: str = "scraper-service"
    SERVICE_PORT: int = 8003
    GRPC_PORT: int = 50053
    
    # Scraper-specific settings
    PLAYWRIGHT_HEADLESS: bool = True
    PLAYWRIGHT_TIMEOUT_MS: int = 30000
    MAX_SCRAPING_WORKERS: int = 5

class AuthServiceSettings(BaseServiceSettings):
    SERVICE_NAME: str = "auth-service"
    SERVICE_PORT: int = 8004
    GRPC_PORT: int = 50054

class ExternalAPISettings(BaseServiceSettings):
    SERVICE_NAME: str = "external-api-adapter"
    SERVICE_PORT: int = 8005
    GRPC_PORT: int = 50055
    
    # API rate limits
    SHOPIFY_RATE_LIMIT: int = 40  # requests per second
    AMAZON_RATE_LIMIT: int = 10
    GOOGLE_RATE_LIMIT: int = 100

class LLMAssistantSettings(BaseServiceSettings):
    SERVICE_NAME: str = "llm-assistant"
    SERVICE_PORT: int = 8006
    GRPC_PORT: int = 50056
    
    # LLM-specific settings
    DEFAULT_MODEL: str = "gemini-pro"
    MAX_TOKENS: int = 4096
    TEMPERATURE: float = 0.7
    ENABLE_REASONING_CHAIN: bool = True

class SchedulerSettings(BaseServiceSettings):
    SERVICE_NAME: str = "scheduler"
    SERVICE_PORT: int = 8007
    GRPC_PORT: int = 50057
    
    # Scheduler-specific settings
    DEFAULT_SCHEDULE_CRON: str = "0 */6 * * *"  # Every 6 hours
    MAX_CONCURRENT_FLOWS: int = 10
    FLOW_TIMEOUT_MINUTES: int = 60

class DataPipelineSettings(BaseServiceSettings):
    SERVICE_NAME: str = "data-pipeline"
    SERVICE_PORT: int = 8008
    GRPC_PORT: int = 50058
    
    # Data processing settings
    SPARK_MASTER: str = "local[*]"
    ENABLE_SPARK: bool = False  # Use Pandas by default
    DATA_QUALITY_THRESHOLD: float = 0.8
    
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
