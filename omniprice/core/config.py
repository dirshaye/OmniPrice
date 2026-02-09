"""
Core Configuration Module for OmniPrice

Technical Explanation:
- Uses Pydantic Settings to load environment variables from .env file
- BaseSettings automatically validates types and required fields
- We define all configuration in one place for consistency
- Each setting has a default value for development
"""

import json
from typing import Optional

from pydantic import field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables
    
    Technical Note:
    - Pydantic will automatically convert env var types (str -> int, str -> bool, etc.)
    - Variables are read from .env file if it exists
    - You can override settings by setting environment variables
    """
    
    # Application Settings
    APP_NAME: str = "OmniPrice"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    ENVIRONMENT: str = "development"  # development, staging, production
    
    # API Settings
    API_V1_PREFIX: str = "/api/v1"
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # MongoDB Database Configuration
    # Technical Note: MongoDB connection string format
    # mongodb://username:password@host:port/database_name
    MONGODB_URL: str = "mongodb://admin:password@localhost:27017"
    MONGODB_DB_NAME: str = "omniprice"

    # Infrastructure (MVP)
    REDIS_URL: str = "redis://localhost:6379/0"
    RABBITMQ_URL: str = "amqp://guest:guest@localhost:5672/"
    RABBITMQ_QUEUE_SCRAPE: str = "scrape.jobs"
    RABBITMQ_QUEUE_SCRAPE_DLQ: str = "scrape.jobs.dlq"
    CACHE_DEFAULT_TTL_SECONDS: int = 300
    
    # JWT Security Settings
    # Technical Note: JWT (JSON Web Tokens) for stateless authentication
    SECRET_KEY: str = "your-secret-key-change-in-production"  # MUST change in .env
    ALGORITHM: str = "HS256"  # HMAC with SHA-256
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # CORS Settings
    # Technical Note: CORS allows frontend (different domain) to call our API
    CORS_ORIGINS: list[str] = ["*"]
    
    # External API Keys
    GEMINI_API_KEY: Optional[str] = None  # Google Gemini AI
    OPENAI_API_KEY: Optional[str] = None  # OpenAI GPT
    
    # Scraper Settings
    SCRAPER_USER_AGENT: str = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    SCRAPER_TIMEOUT: int = 10  # seconds
    SCRAPER_MAX_RETRIES: int = 3
    SCRAPER_MAX_JOB_RETRIES: int = 3
    SCRAPER_BACKOFF_BASE_SECONDS: int = 2
    SCRAPER_CHECK_INTERVAL_MINUTES: int = 15
    SCRAPER_ENFORCE_DOMAIN_ALLOWLIST: bool = False
    SCRAPER_ALLOWED_DOMAINS: list[str] = []
    
    # Logging
    LOG_LEVEL: str = "INFO"  # DEBUG, INFO, WARNING, ERROR, CRITICAL

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        extra="ignore",
    )

    @field_validator("DEBUG", mode="before")
    @classmethod
    def _parse_debug(cls, value):
        if isinstance(value, bool):
            return value
        if value is None:
            return False
        if isinstance(value, str):
            normalized = value.strip().lower()
            if normalized in {"1", "true", "yes", "on"}:
                return True
            if normalized in {"0", "false", "no", "off"}:
                return False
        # Defensive fallback: invalid debug values should not crash startup.
        return False

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def _parse_cors_origins(cls, value):
        if isinstance(value, str):
            stripped = value.strip()
            if not stripped:
                return []
            # Accept JSON array form and comma-separated form.
            if stripped.startswith("["):
                try:
                    parsed = json.loads(stripped)
                    if isinstance(parsed, list):
                        return [str(item).strip() for item in parsed if str(item).strip()]
                except Exception:
                    pass
            return [part.strip() for part in stripped.split(",") if part.strip()]
        if isinstance(value, (list, tuple, set)):
            return [str(item).strip() for item in value if str(item).strip()]
        return value

    @field_validator("SCRAPER_ALLOWED_DOMAINS", mode="before")
    @classmethod
    def _parse_scraper_allowed_domains(cls, value):
        if isinstance(value, str):
            stripped = value.strip()
            if not stripped:
                return []
            return [part.strip().lower() for part in stripped.split(",") if part.strip()]
        if isinstance(value, (list, tuple, set)):
            return [str(item).strip().lower() for item in value if str(item).strip()]
        return value

    @field_validator("ENVIRONMENT")
    @classmethod
    def _validate_environment(cls, value: str) -> str:
        allowed = {"development", "staging", "production", "test"}
        normalized = value.strip().lower()
        if normalized not in allowed:
            raise ValueError(f"ENVIRONMENT must be one of {sorted(allowed)}")
        return normalized

    @model_validator(mode="after")
    def _validate_production_secrets(self):
        if self.ENVIRONMENT == "production":
            insecure_defaults = {
                "your-secret-key-change-in-production",
                "change-me-in-production",
            }
            if not self.SECRET_KEY or self.SECRET_KEY in insecure_defaults:
                raise ValueError("SECRET_KEY must be set to a strong non-default value in production")
            if not self.MONGODB_URL:
                raise ValueError("MONGODB_URL must be set in production")
        return self


# Singleton instance
# Technical Note: We create one global settings instance
# This is loaded once when the app starts and reused everywhere
settings = Settings()


# Helper function to get settings
def get_settings() -> Settings:
    """
    Dependency injection helper for FastAPI
    
    Usage in FastAPI route:
    @router.get("/")
    async def read_root(settings: Settings = Depends(get_settings)):
        return {"app_name": settings.APP_NAME}
    """
    return settings
