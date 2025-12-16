"""
Core Module - Shared Infrastructure

This module contains all shared functionality:
- config: Application settings and environment variables
- database: MongoDB connection and helpers
- cache: Redis caching layer
- security: Authentication, JWT, password hashing
- exceptions: Custom exception classes
- dependencies: FastAPI dependency injection helpers
"""

from omniprice.core.config import settings, get_settings
from omniprice.core.database import (
    get_database,
    get_collection,
    connect_to_mongodb,
    close_mongodb_connection,
    Collections,
)
from omniprice.core.cache import (
    get_cache_service,
    CacheService,
    connect_to_redis,
    close_redis_connection,
)
from omniprice.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    get_current_user_id,
)
from omniprice.core.exceptions import (
    NotFoundException,
    BadRequestException,
    UnauthorizedException,
    ForbiddenException,
    ConflictException,
    ValidationException,
)
from omniprice.core.dependencies import (
    DatabaseDep,
    CacheDep,
    SettingsDep,
    CurrentUserDep,
)

__all__ = [
    # Config
    "settings",
    "get_settings",
    # Database
    "get_database",
    "get_collection",
    "connect_to_mongodb",
    "close_mongodb_connection",
    "Collections",
    # Cache
    "get_cache_service",
    "CacheService",
    "connect_to_redis",
    "close_redis_connection",
    # Security
    "hash_password",
    "verify_password",
    "create_access_token",
    "create_refresh_token",
    "get_current_user_id",
    # Exceptions
    "NotFoundException",
    "BadRequestException",
    "UnauthorizedException",
    "ForbiddenException",
    "ConflictException",
    "ValidationException",
    # Dependencies
    "DatabaseDep",
    "CacheDep",
    "SettingsDep",
    "CurrentUserDep",
]
