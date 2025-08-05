"""
Structured logging setup - Enterprise standard for observability.
JSON structured logs for centralized logging systems.
"""

import json
import logging
import sys
from datetime import datetime
from typing import Any, Dict, Optional
import traceback


class StructuredFormatter(logging.Formatter):
    """JSON formatter for structured logging"""
    
    def __init__(self, service_name: str, service_version: str = "1.0.0"):
        self.service_name = service_name
        self.service_version = service_version
        super().__init__()
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON"""
        log_entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "service": self.service_name,
            "service_version": self.service_version,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        # Add exception info if present
        if record.exc_info:
            log_entry["exception"] = {
                "type": record.exc_info[0].__name__,
                "message": str(record.exc_info[1]),
                "traceback": traceback.format_exception(*record.exc_info)
            }
        
        # Add extra fields
        if hasattr(record, "extra_fields"):
            log_entry.update(record.extra_fields)
        
        # Add correlation ID if present (for distributed tracing)
        if hasattr(record, "correlation_id"):
            log_entry["correlation_id"] = record.correlation_id
        
        return json.dumps(log_entry, ensure_ascii=False)


def setup_structured_logging(
    service_name: str,
    level: str = "INFO",
    service_version: str = "1.0.0"
) -> None:
    """
    Setup structured logging for a microservice.
    
    Args:
        service_name: Name of the service
        level: Logging level
        service_version: Version of the service
    """
    # Remove existing handlers
    root_logger = logging.getLogger()
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Setup structured formatter
    formatter = StructuredFormatter(service_name, service_version)
    
    # Setup console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    
    # Configure root logger
    root_logger.setLevel(getattr(logging, level.upper()))
    root_logger.addHandler(console_handler)
    
    # Suppress some noisy loggers
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("grpc").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance with structured formatting"""
    return logging.getLogger(name)


class LoggingContextManager:
    """Context manager for adding fields to all logs within a context"""
    
    def __init__(self, **fields):
        self.fields = fields
        self.old_factory = logging.getLogRecordFactory()
    
    def __enter__(self):
        def record_factory(*args, **kwargs):
            record = self.old_factory(*args, **kwargs)
            if not hasattr(record, "extra_fields"):
                record.extra_fields = {}
            record.extra_fields.update(self.fields)
            return record
        
        logging.setLogRecordFactory(record_factory)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        logging.setLogRecordFactory(self.old_factory)


def with_correlation_id(correlation_id: str):
    """Add correlation ID to all logs within context"""
    return LoggingContextManager(correlation_id=correlation_id)


def with_user_context(user_id: str, user_email: Optional[str] = None):
    """Add user context to all logs"""
    fields = {"user_id": user_id}
    if user_email:
        fields["user_email"] = user_email
    return LoggingContextManager(**fields)


class LoggingMiddleware:
    """Middleware to add request context to logs"""
    
    def __init__(self, app, service_name: str):
        self.app = app
        self.service_name = service_name
        self.logger = get_logger(f"{service_name}.middleware")
    
    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            request_id = scope.get("headers", {}).get("x-request-id", "unknown")
            
            with LoggingContextManager(
                request_id=request_id,
                method=scope["method"],
                path=scope["path"],
                service=self.service_name
            ):
                self.logger.info("Request started")
                try:
                    await self.app(scope, receive, send)
                    self.logger.info("Request completed")
                except Exception as e:
                    self.logger.error("Request failed", exc_info=True)
                    raise
        else:
            await self.app(scope, receive, send)
