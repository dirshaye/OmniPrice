"""
Enterprise-grade error handling for microservices.
Standardized error responses following REST API best practices.
"""

from typing import Optional, Dict, Any, List
from fastapi import HTTPException
from pydantic import BaseModel


class ErrorDetail(BaseModel):
    """Individual error detail"""
    field: Optional[str] = None
    message: str
    code: Optional[str] = None


class ErrorResponse(BaseModel):
    """Standardized error response format"""
    error: str
    message: str
    details: Optional[List[ErrorDetail]] = None
    timestamp: str
    request_id: Optional[str] = None
    service: Optional[str] = None


class APIError(HTTPException):
    """Base API error with enhanced context"""
    
    def __init__(
        self,
        status_code: int,
        error: str,
        message: str,
        details: Optional[List[ErrorDetail]] = None,
        headers: Optional[Dict[str, str]] = None
    ):
        self.error = error
        self.message = message
        self.details = details or []
        super().__init__(status_code=status_code, detail=message, headers=headers)


class ValidationError(APIError):
    """Validation error (400)"""
    
    def __init__(
        self,
        message: str = "Validation failed",
        details: Optional[List[ErrorDetail]] = None
    ):
        super().__init__(
            status_code=400,
            error="VALIDATION_ERROR",
            message=message,
            details=details
        )


class NotFoundError(APIError):
    """Resource not found error (404)"""
    
    def __init__(
        self,
        resource: str,
        identifier: Optional[str] = None
    ):
        message = f"{resource} not found"
        if identifier:
            message += f" with id: {identifier}"
        
        super().__init__(
            status_code=404,
            error="NOT_FOUND",
            message=message
        )


class UnauthorizedError(APIError):
    """Unauthorized access error (401)"""
    
    def __init__(self, message: str = "Unauthorized access"):
        super().__init__(
            status_code=401,
            error="UNAUTHORIZED",
            message=message,
            headers={"WWW-Authenticate": "Bearer"}
        )


class ForbiddenError(APIError):
    """Forbidden access error (403)"""
    
    def __init__(self, message: str = "Access forbidden"):
        super().__init__(
            status_code=403,
            error="FORBIDDEN",
            message=message
        )


class ConflictError(APIError):
    """Conflict error (409)"""
    
    def __init__(self, message: str, resource: Optional[str] = None):
        error_msg = message
        if resource:
            error_msg = f"{resource} conflict: {message}"
        
        super().__init__(
            status_code=409,
            error="CONFLICT",
            message=error_msg
        )


class ServiceUnavailableError(APIError):
    """Service unavailable error (503)"""
    
    def __init__(self, service_name: str, message: Optional[str] = None):
        error_msg = message or f"{service_name} service is currently unavailable"
        
        super().__init__(
            status_code=503,
            error="SERVICE_UNAVAILABLE",
            message=error_msg
        )


class RateLimitError(APIError):
    """Rate limit exceeded error (429)"""
    
    def __init__(self, retry_after: Optional[int] = None):
        headers = {}
        if retry_after:
            headers["Retry-After"] = str(retry_after)
        
        super().__init__(
            status_code=429,
            error="RATE_LIMIT_EXCEEDED",
            message="Rate limit exceeded. Please try again later.",
            headers=headers
        )


class BusinessLogicError(APIError):
    """Business logic error (422)"""
    
    def __init__(self, message: str, code: Optional[str] = None):
        super().__init__(
            status_code=422,
            error=code or "BUSINESS_LOGIC_ERROR",
            message=message
        )


# Error code mappings for consistent error handling
ERROR_CODES = {
    "USER_NOT_FOUND": (404, "User not found"),
    "PRODUCT_NOT_FOUND": (404, "Product not found"),
    "INVALID_CREDENTIALS": (401, "Invalid credentials"),
    "INSUFFICIENT_PERMISSIONS": (403, "Insufficient permissions"),
    "DUPLICATE_RESOURCE": (409, "Resource already exists"),
    "INVALID_INPUT": (400, "Invalid input data"),
    "EXTERNAL_SERVICE_ERROR": (502, "External service error"),
    "DATABASE_ERROR": (500, "Database operation failed"),
    "INVALID_PRICE": (400, "Invalid price value"),
    "PRODUCT_ALREADY_EXISTS": (409, "Product with this SKU already exists"),
}


def create_error_from_code(code: str, details: Optional[str] = None) -> APIError:
    """Create standardized error from error code"""
    if code not in ERROR_CODES:
        return APIError(500, "UNKNOWN_ERROR", f"Unknown error: {code}")
    
    status_code, default_message = ERROR_CODES[code]
    message = details or default_message
    
    return APIError(status_code, code, message)
