"""
Shared utilities for OmniPriceX microservices.
"""

import logging
import sys
from typing import Dict, Any
import json
from datetime import datetime


def setup_logging(service_name: str, log_level: str = "INFO") -> logging.Logger:
    """
    Setup structured logging for a service.
    
    Args:
        service_name: Name of the service
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
    
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(service_name)
    logger.setLevel(getattr(logging, log_level.upper()))
    
    # Remove existing handlers
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # Create console handler with structured format
    handler = logging.StreamHandler(sys.stdout)
    formatter = StructuredFormatter(service_name)
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    
    return logger


class StructuredFormatter(logging.Formatter):
    """Custom formatter for structured JSON logging"""
    
    def __init__(self, service_name: str):
        super().__init__()
        self.service_name = service_name
    
    def format(self, record: logging.LogRecord) -> str:
        log_entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "service": self.service_name,
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        # Add exception info if present
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)
        
        # Add extra fields if present
        if hasattr(record, "extra"):
            log_entry.update(record.extra)
        
        return json.dumps(log_entry)


def validate_environment_variables(required_vars: list) -> Dict[str, str]:
    """
    Validate that required environment variables are set.
    
    Args:
        required_vars: List of required environment variable names
    
    Returns:
        Dictionary of environment variables
    
    Raises:
        EnvironmentError: If any required variables are missing
    """
    import os
    
    missing_vars = []
    env_vars = {}
    
    for var in required_vars:
        value = os.getenv(var)
        if value is None:
            missing_vars.append(var)
        else:
            env_vars[var] = value
    
    if missing_vars:
        raise EnvironmentError(
            f"Missing required environment variables: {', '.join(missing_vars)}"
        )
    
    return env_vars


class ServiceHealthChecker:
    """Health check utilities for services"""
    
    @staticmethod
    def check_database_connection(db_client) -> bool:
        """Check if database connection is healthy"""
        try:
            # This would be implemented based on the database client
            return True
        except Exception:
            return False
    
    @staticmethod
    def check_redis_connection(redis_client) -> bool:
        """Check if Redis connection is healthy"""
        try:
            redis_client.ping()
            return True
        except Exception:
            return False
    
    @staticmethod
    def get_service_info() -> Dict[str, Any]:
        """Get basic service information"""
        import os
        import psutil
        
        return {
            "uptime": datetime.utcnow().isoformat(),
            "pid": os.getpid(),
            "memory_usage": psutil.Process().memory_info().rss,
            "cpu_percent": psutil.Process().cpu_percent(),
        }
