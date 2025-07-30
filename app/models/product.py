from beanie import Document, Indexed
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum
import uuid

class ProductStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    DISCONTINUED = "discontinued"

class Product(Document):
    """Product model for pricing management"""
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), alias="_id")
    
    # Basic information
    name: str = Field(..., min_length=1, max_length=200)
    sku: Indexed(str, unique=True)
    description: Optional[str] = None
    category: Optional[str] = None
    brand: Optional[str] = None
    
    # Pricing information
    base_price: float = Field(..., gt=0)
    current_price: float = Field(..., gt=0)
    min_price: float = Field(..., gt=0)
    max_price: float = Field(..., gt=0)
    cost_price: Optional[float] = Field(None, gt=0)
    
    # Inventory
    stock_quantity: int = Field(default=0, ge=0)
    low_stock_threshold: int = Field(default=10, ge=0)
    
    # Status and metadata
    status: ProductStatus = ProductStatus.ACTIVE
    is_active: bool = True
    
    # Competitor tracking
    competitor_urls: Dict[str, str] = Field(default_factory=dict)  # competitor_id: url
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: Optional[str] = None  # User ID
    
    # Additional metadata
    tags: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    class Settings:
        name = "products"
        indexes = [
            "sku",
            "category",
            "brand",
            "is_active",
            "status",
            "created_at"
        ]
    
    def __str__(self):
        return f"{self.name} ({self.sku})"
    
    @property
    def profit_margin(self) -> Optional[float]:
        """Calculate profit margin percentage"""
        if self.cost_price and self.current_price:
            return ((self.current_price - self.cost_price) / self.current_price) * 100
        return None
    
    @property
    def is_low_stock(self) -> bool:
        """Check if product is low in stock"""
        return self.stock_quantity <= self.low_stock_threshold

class ProductCreate(BaseModel):
    """Schema for creating products"""
    name: str = Field(..., min_length=1, max_length=200)
    sku: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    category: Optional[str] = None
    brand: Optional[str] = None
    base_price: float = Field(..., gt=0)
    current_price: float = Field(..., gt=0)
    min_price: float = Field(..., gt=0)
    max_price: float = Field(..., gt=0)
    cost_price: Optional[float] = Field(None, gt=0)
    stock_quantity: int = Field(default=0, ge=0)
    low_stock_threshold: int = Field(default=10, ge=0)
    competitor_urls: Dict[str, str] = Field(default_factory=dict)
    tags: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)

class ProductUpdate(BaseModel):
    """Schema for updating products"""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    category: Optional[str] = None
    brand: Optional[str] = None
    base_price: Optional[float] = Field(None, gt=0)
    current_price: Optional[float] = Field(None, gt=0)
    min_price: Optional[float] = Field(None, gt=0)
    max_price: Optional[float] = Field(None, gt=0)
    cost_price: Optional[float] = Field(None, gt=0)
    stock_quantity: Optional[int] = Field(None, ge=0)
    low_stock_threshold: Optional[int] = Field(None, ge=0)
    status: Optional[ProductStatus] = None
    is_active: Optional[bool] = None
    competitor_urls: Optional[Dict[str, str]] = None
    tags: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None

class ProductResponse(BaseModel):
    """Schema for product responses"""
    id: str
    name: str
    sku: str
    description: Optional[str]
    category: Optional[str]
    brand: Optional[str]
    base_price: float
    current_price: float
    min_price: float
    max_price: float
    cost_price: Optional[float]
    stock_quantity: int
    low_stock_threshold: int
    status: ProductStatus
    is_active: bool
    profit_margin: Optional[float]
    is_low_stock: bool
    competitor_urls: Dict[str, str]
    tags: List[str]
    created_at: datetime
    updated_at: datetime

class ProductSummary(BaseModel):
    """Simplified product schema for lists"""
    id: str
    name: str
    sku: str
    category: Optional[str]
    current_price: float
    stock_quantity: int
    is_active: bool
    profit_margin: Optional[float]
    is_low_stock: bool
