"""
Custom Exception Classes

Technical Explanation:
- Custom exceptions provide better error handling
- Each exception has specific HTTP status code
- FastAPI can automatically convert these to proper HTTP responses
- Makes debugging easier with meaningful error messages
"""

from fastapi import HTTPException, status


class OmniPriceException(Exception):
    """
    Base exception for all OmniPrice errors
    
    Technical Note: All custom exceptions inherit from this
    Makes it easy to catch all app-specific errors
    """
    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class NotFoundException(OmniPriceException):
    """
    Resource not found exception
    
    Usage:
        product = await db.products.find_one({"_id": product_id})
        if not product:
            raise NotFoundException(f"Product {product_id} not found")
    """
    def __init__(self, message: str = "Resource not found"):
        super().__init__(message, status_code=status.HTTP_404_NOT_FOUND)


class BadRequestException(OmniPriceException):
    """
    Bad request exception (invalid input)
    
    Usage:
        if price < 0:
            raise BadRequestException("Price cannot be negative")
    """
    def __init__(self, message: str = "Bad request"):
        super().__init__(message, status_code=status.HTTP_400_BAD_REQUEST)


class UnauthorizedException(OmniPriceException):
    """
    Unauthorized exception (authentication failed)
    
    Usage:
        if not verify_password(input_password, stored_hash):
            raise UnauthorizedException("Invalid credentials")
    """
    def __init__(self, message: str = "Unauthorized"):
        super().__init__(message, status_code=status.HTTP_401_UNAUTHORIZED)


class ForbiddenException(OmniPriceException):
    """
    Forbidden exception (no permission)
    
    Usage:
        if user.role != "admin":
            raise ForbiddenException("Admin access required")
    """
    def __init__(self, message: str = "Forbidden"):
        super().__init__(message, status_code=status.HTTP_403_FORBIDDEN)


class ConflictException(OmniPriceException):
    """
    Conflict exception (duplicate resource)
    
    Usage:
        existing = await db.users.find_one({"email": email})
        if existing:
            raise ConflictException("Email already registered")
    """
    def __init__(self, message: str = "Resource already exists"):
        super().__init__(message, status_code=status.HTTP_409_CONFLICT)


class ServiceUnavailableException(OmniPriceException):
    """
    Service unavailable exception
    
    Usage:
        if not redis_client:
            raise ServiceUnavailableException("Cache service unavailable")
    """
    def __init__(self, message: str = "Service temporarily unavailable"):
        super().__init__(message, status_code=status.HTTP_503_SERVICE_UNAVAILABLE)


class ValidationException(OmniPriceException):
    """
    Validation exception (business logic validation)
    
    Usage:
        if product.price > product.cost * 10:
            raise ValidationException("Price cannot be more than 10x cost")
    """
    def __init__(self, message: str = "Validation failed"):
        super().__init__(message, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)


# Helper function to convert exceptions to HTTP responses
def exception_to_http_response(exc: OmniPriceException) -> HTTPException:
    """
    Convert custom exception to FastAPI HTTPException
    
    Technical Note: FastAPI automatically handles HTTPException
    This helper converts our custom exceptions to HTTPException
    
    Usage in FastAPI exception handler:
        @app.exception_handler(OmniPriceException)
        async def omniprice_exception_handler(request, exc):
            raise exception_to_http_response(exc)
    """
    return HTTPException(
        status_code=exc.status_code,
        detail=exc.message
    )
