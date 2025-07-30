from beanie import Document, Indexed
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum
import uuid

class CompetitorStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"

class Competitor(Document):
    """Competitor model for tracking competitor information"""
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), alias="_id")
    
    # Basic information
    name: str = Field(..., min_length=1, max_length=100)
    domain: Indexed(str, unique=True)
    website_url: Optional[str] = None
    description: Optional[str] = None
    
    # Status
    status: CompetitorStatus = CompetitorStatus.ACTIVE
    is_active: bool = True
    
    # Scraping configuration
    scraping_enabled: bool = True
    scraping_frequency: int = Field(default=3600, gt=0)  # seconds
    user_agent: Optional[str] = None
    headers: Dict[str, str] = Field(default_factory=dict)
    
    # Rate limiting for scraping
    delay_min: int = Field(default=1, ge=0)
    delay_max: int = Field(default=3, ge=0)
    concurrent_requests: int = Field(default=1, ge=1)
    
    # Scraping status
    last_scraped: Optional[datetime] = None
    last_successful_scrape: Optional[datetime] = None
    consecutive_failures: int = Field(default=0, ge=0)
    total_scrapes: int = Field(default=0, ge=0)
    successful_scrapes: int = Field(default=0, ge=0)
    
    # Configuration
    selectors: Dict[str, str] = Field(default_factory=dict)  # CSS selectors for data extraction
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: Optional[str] = None  # User ID
    
    # Additional metadata
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    class Settings:
        name = "competitors"
        indexes = [
            "domain",
            "name",
            "is_active",
            "status",
            "scraping_enabled"
        ]
    
    def __str__(self):
        return f"{self.name} ({self.domain})"
    
    @property
    def success_rate(self) -> float:
        """Calculate scraping success rate"""
        if self.total_scrapes == 0:
            return 0.0
        return (self.successful_scrapes / self.total_scrapes) * 100

class CompetitorCreate(BaseModel):
    """Schema for creating competitors"""
    name: str = Field(..., min_length=1, max_length=100)
    domain: str = Field(..., min_length=1)
    website_url: Optional[str] = None
    description: Optional[str] = None
    scraping_enabled: bool = True
    scraping_frequency: int = Field(default=3600, gt=0)
    user_agent: Optional[str] = None
    headers: Dict[str, str] = Field(default_factory=dict)
    delay_min: int = Field(default=1, ge=0)
    delay_max: int = Field(default=3, ge=0)
    concurrent_requests: int = Field(default=1, ge=1)
    selectors: Dict[str, str] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)

class CompetitorUpdate(BaseModel):
    """Schema for updating competitors"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    website_url: Optional[str] = None
    description: Optional[str] = None
    status: Optional[CompetitorStatus] = None
    is_active: Optional[bool] = None
    scraping_enabled: Optional[bool] = None
    scraping_frequency: Optional[int] = Field(None, gt=0)
    user_agent: Optional[str] = None
    headers: Optional[Dict[str, str]] = None
    delay_min: Optional[int] = Field(None, ge=0)
    delay_max: Optional[int] = Field(None, ge=0)
    concurrent_requests: Optional[int] = Field(None, ge=1)
    selectors: Optional[Dict[str, str]] = None
    metadata: Optional[Dict[str, Any]] = None

class CompetitorResponse(BaseModel):
    """Schema for competitor responses"""
    id: str
    name: str
    domain: str
    website_url: Optional[str]
    description: Optional[str]
    status: CompetitorStatus
    is_active: bool
    scraping_enabled: bool
    scraping_frequency: int
    last_scraped: Optional[datetime]
    last_successful_scrape: Optional[datetime]
    consecutive_failures: int
    success_rate: float
    total_scrapes: int
    successful_scrapes: int
    created_at: datetime
    updated_at: datetime

class CompetitorProduct(BaseModel):
    """Schema for competitor product pricing data"""
    competitor_id: str
    competitor_name: str
    product_url: str
    current_price: Optional[float]
    original_price: Optional[float]
    discount_percentage: Optional[float]
    availability: str = "unknown"  # in_stock, out_of_stock, limited, unknown
    last_updated: datetime
    currency: str = "USD"
    
    # Additional scraped data
    title: Optional[str] = None
    description: Optional[str] = None
    image_url: Optional[str] = None
    rating: Optional[float] = None
    review_count: Optional[int] = None
    shipping_info: Optional[str] = None
    
    # Scraping metadata
    scrape_duration: Optional[float] = None
    http_status: Optional[int] = None
    error_message: Optional[str] = None
