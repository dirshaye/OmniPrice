"""
Shared data models for OmniPriceX microservices.
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum
from pydantic import BaseModel, Field
from beanie import Document


class PriceHistoryEntry(BaseModel):
    """Price history entry model"""
    price: float
    timestamp: datetime
    source: str
    competitor_id: Optional[str] = None


class ProductStatus(str, Enum):
    """Product status enumeration"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    DISCONTINUED = "discontinued"
    OUT_OF_STOCK = "out_of_stock"


class PricingRuleType(str, Enum):
    """Pricing rule type enumeration"""
    FIXED = "fixed"
    PERCENTAGE_MARKUP = "percentage_markup"
    COMPETITOR_BASED = "competitor_based"
    DYNAMIC = "dynamic"


class JobStatus(str, Enum):
    """Job status enumeration"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class BaseDocument(Document):
    """Base document class with common fields"""
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        use_state_management = True


class Product(BaseDocument):
    """Product document model"""
    name: str
    sku: str = Field(unique=True)
    description: Optional[str] = None
    category: str
    brand: Optional[str] = None
    base_price: float
    current_price: float
    status: ProductStatus = ProductStatus.ACTIVE
    price_history: List[PriceHistoryEntry] = []
    metadata: Dict[str, Any] = {}
    
    class Settings:
        name = "products"


class PricingRule(BaseDocument):
    """Pricing rule document model"""
    name: str
    product_id: str
    rule_type: PricingRuleType
    parameters: Dict[str, Any]
    is_active: bool = True
    priority: int = 0
    
    class Settings:
        name = "pricing_rules"


class Competitor(BaseDocument):
    """Competitor document model"""
    name: str
    website: str
    status: str = "active"
    metadata: Dict[str, Any] = {}
    
    class Settings:
        name = "competitors"


class ScrapeJob(BaseDocument):
    """Scrape job document model"""
    competitor_id: str
    product_urls: List[str]
    status: JobStatus = JobStatus.PENDING
    scheduled_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    results: List[Dict[str, Any]] = []
    error_message: Optional[str] = None
    
    class Settings:
        name = "scrape_jobs"


class User(BaseDocument):
    """User document model"""
    email: str = Field(unique=True)
    hashed_password: str
    full_name: str
    is_active: bool = True
    is_superuser: bool = False
    last_login: Optional[datetime] = None
    
    class Settings:
        name = "users"


class APIResponse(BaseModel):
    """Standard API response model"""
    success: bool
    message: str
    data: Optional[Any] = None
    errors: Optional[List[str]] = None


class PaginatedResponse(BaseModel):
    """Paginated response model"""
    items: List[Any]
    total: int
    page: int
    size: int
    pages: int
