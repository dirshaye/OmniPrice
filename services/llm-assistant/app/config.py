from functools import lru_cache
from pydantic_settings import BaseSettings
from typing import Optional, List

class Settings(BaseSettings):
    """
    LLM Assistant Service Configuration
    """
    # Database
    MONGODB_URL: str = "mongodb+srv://dirshaye:dre%40mongodb@cluster0.jgxe61g.mongodb.net/omnipricex_llm?retryWrites=true&w=majority&appName=Cluster0"
    DATABASE_NAME: str = "omnipricex_llm"
    
    # API Settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "OmniPriceX LLM Assistant"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "AI-powered pricing insights and recommendations service"
    
    # LLM Provider Settings
    OPENAI_API_KEY: Optional[str] = None
    GEMINI_API_KEY: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None
    
    # Default LLM Configuration
    DEFAULT_LLM_PROVIDER: str = "gemini"  # gemini, openai, anthropic
    DEFAULT_MODEL: str = "gemini-1.5-flash"
    MAX_TOKENS: int = 2048
    TEMPERATURE: float = 0.7
    
    # CORS Settings
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:8080", 
        "http://localhost:5173",
        "http://localhost:8001"  # Auth service
    ]
    
    # Environment
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 100
    RATE_LIMIT_PER_HOUR: int = 1000
    
    # Service Communication
    AUTH_SERVICE_URL: str = "http://localhost:8001"
    PRODUCT_SERVICE_URL: str = "http://localhost:8002"
    PRICING_SERVICE_URL: str = "http://localhost:8003"
    
    # Caching
    CACHE_TTL_SECONDS: int = 300  # 5 minutes
    
    class Config:
        env_file = ".env"
        case_sensitive = True

@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()

# Global settings instance
settings = get_settings()
