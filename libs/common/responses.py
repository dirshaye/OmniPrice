"""
Enterprise API response schemas following industry standards.
Consistent response format across all microservices.
"""

from typing import Generic, TypeVar, List, Optional, Any, Dict
from pydantic import BaseModel, Field
from datetime import datetime

T = TypeVar('T')


class APIResponse(BaseModel, Generic[T]):
    """Standard API response wrapper"""
    success: bool = Field(True, description="Request success status")
    data: T = Field(..., description="Response data")
    message: Optional[str] = Field(None, description="Response message")
    request_id: Optional[str] = Field(None, description="Request correlation ID")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Response timestamp")


class PaginationMeta(BaseModel):
    """Pagination metadata"""
    page: int = Field(..., description="Current page number")
    per_page: int = Field(..., description="Items per page")
    total: int = Field(..., description="Total number of items")
    pages: int = Field(..., description="Total number of pages")
    has_next: bool = Field(..., description="Has next page")
    has_prev: bool = Field(..., description="Has previous page")


class PaginatedResponse(BaseModel, Generic[T]):
    """Paginated response wrapper"""
    success: bool = Field(True, description="Request success status")
    data: List[T] = Field(..., description="Response data items")
    meta: PaginationMeta = Field(..., description="Pagination metadata")
    message: Optional[str] = Field(None, description="Response message")
    request_id: Optional[str] = Field(None, description="Request correlation ID")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Response timestamp")


class ErrorResponse(BaseModel):
    """Standard error response"""
    success: bool = Field(False, description="Request success status")
    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Error message")
    details: Optional[List[Dict[str, Any]]] = Field(None, description="Error details")
    request_id: Optional[str] = Field(None, description="Request correlation ID")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Error timestamp")
    service: Optional[str] = Field(None, description="Service that generated the error")


class HealthResponse(BaseModel):
    """Health check response"""
    service: str = Field(..., description="Service name")
    status: str = Field(..., description="Health status")
    timestamp: float = Field(..., description="Check timestamp")
    uptime_seconds: float = Field(..., description="Service uptime in seconds")
    version: Optional[str] = Field(None, description="Service version")
    checks: Optional[List[Dict[str, Any]]] = Field(None, description="Individual health checks")
