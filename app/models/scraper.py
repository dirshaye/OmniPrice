from beanie import Document
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum
import uuid

class JobType(str, Enum):
    SINGLE_PRODUCT = "single_product"
    COMPETITOR_BULK = "competitor_bulk"
    CATEGORY_SCAN = "category_scan"
    PRICE_CHECK = "price_check"
    FULL_COMPETITOR = "full_competitor"

class JobStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    RETRYING = "retrying"

class ErrorType(str, Enum):
    HTTP_ERROR = "http_error"
    PARSING_ERROR = "parsing_error"
    TIMEOUT = "timeout"
    ANTI_BOT = "anti_bot"
    RATE_LIMIT = "rate_limit"
    NETWORK_ERROR = "network_error"
    VALIDATION_ERROR = "validation_error"
    UNKNOWN = "unknown"

# Scrape Job Model
class ScrapeJob(Document):
    """Track scraping jobs and their status"""
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), alias="_id")
    
    # Job details
    job_type: JobType
    name: Optional[str] = None
    description: Optional[str] = None
    
    # Target information
    target_urls: List[str] = Field(default_factory=list)
    competitor_id: Optional[str] = None
    competitor_name: Optional[str] = None
    product_ids: List[str] = Field(default_factory=list)
    
    # Configuration
    scraper_config: Dict[str, Any] = Field(default_factory=dict)
    priority: int = Field(default=0, ge=0)
    
    # Status tracking
    status: JobStatus = JobStatus.PENDING
    progress: float = Field(default=0.0, ge=0, le=100)
    
    # Results
    items_total: int = Field(default=0, ge=0)
    items_scraped: int = Field(default=0, ge=0)
    items_failed: int = Field(default=0, ge=0)
    items_skipped: int = Field(default=0, ge=0)
    
    # Data
    results: List[Dict[str, Any]] = Field(default_factory=list)
    error_summary: Dict[str, int] = Field(default_factory=dict)
    
    # Timing
    created_at: datetime = Field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    estimated_duration: Optional[int] = None  # seconds
    
    # Execution context
    created_by: Optional[str] = None  # User ID
    celery_task_id: Optional[str] = None
    worker_id: Optional[str] = None
    
    # Retry configuration
    max_retries: int = Field(default=3, ge=0)
    retry_count: int = Field(default=0, ge=0)
    retry_delay: int = Field(default=60, ge=0)  # seconds
    
    # Performance metrics
    total_requests: int = Field(default=0, ge=0)
    successful_requests: int = Field(default=0, ge=0)
    avg_response_time: Optional[float] = None  # seconds
    
    class Settings:
        name = "scrape_jobs"
        indexes = [
            "status",
            "job_type",
            "competitor_id",
            "created_at",
            "celery_task_id"
        ]
    
    def __str__(self):
        return f"{self.job_type} - {self.status} ({self.created_at.strftime('%Y-%m-%d %H:%M')})"
    
    @property
    def duration(self) -> Optional[int]:
        """Calculate job duration in seconds"""
        if self.started_at and self.completed_at:
            return int((self.completed_at - self.started_at).total_seconds())
        return None
    
    @property
    def success_rate(self) -> float:
        """Calculate success rate percentage"""
        if self.items_total == 0:
            return 0.0
        return (self.items_scraped / self.items_total) * 100

# Scraping Error Model
class ScrapingError(Document):
    """Log scraping errors for analysis"""
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), alias="_id")
    
    # Job reference
    scrape_job_id: str = Field(..., index=True)
    
    # Error details
    error_type: ErrorType
    error_message: str
    error_code: Optional[str] = None
    http_status: Optional[int] = None
    
    # Request context
    url: str
    method: str = "GET"
    headers: Optional[Dict[str, str]] = Field(default_factory=dict)
    payload: Optional[Dict[str, Any]] = None
    
    # Response context
    response_text: Optional[str] = None
    response_headers: Optional[Dict[str, str]] = Field(default_factory=dict)
    response_time: Optional[float] = None  # seconds
    
    # Product/competitor context
    competitor_id: Optional[str] = None
    competitor_name: Optional[str] = None
    product_id: Optional[str] = None
    product_sku: Optional[str] = None
    
    # Error context
    stack_trace: Optional[str] = None
    browser_logs: Optional[List[str]] = Field(default_factory=list)
    screenshot_url: Optional[str] = None
    
    # Retry information
    retry_count: int = Field(default=0, ge=0)
    will_retry: bool = False
    
    # Timestamps
    timestamp: datetime = Field(default_factory=datetime.utcnow, index=True)
    
    class Settings:
        name = "scraping_errors"
        indexes = [
            "scrape_job_id",
            "error_type",
            "competitor_id",
            "timestamp"
        ]
    
    def __str__(self):
        return f"{self.error_type} - {self.url[:50]}..."

# Scraped Data Model
class ScrapedData(Document):
    """Store scraped product data"""
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), alias="_id")
    
    # Source information
    scrape_job_id: str = Field(..., index=True)
    competitor_id: str = Field(..., index=True)
    competitor_name: str
    source_url: str
    
    # Product identification
    product_id: Optional[str] = None
    product_sku: Optional[str] = None
    competitor_product_id: Optional[str] = None
    
    # Scraped product data
    title: Optional[str] = None
    description: Optional[str] = None
    brand: Optional[str] = None
    category: Optional[str] = None
    
    # Pricing data
    price: Optional[float] = Field(None, ge=0)
    original_price: Optional[float] = Field(None, ge=0)
    discount_amount: Optional[float] = Field(None, ge=0)
    discount_percentage: Optional[float] = Field(None, ge=0, le=100)
    currency: str = "USD"
    
    # Availability
    in_stock: Optional[bool] = None
    stock_quantity: Optional[int] = Field(None, ge=0)
    availability_text: Optional[str] = None
    
    # Additional data
    images: List[str] = Field(default_factory=list)
    rating: Optional[float] = Field(None, ge=0, le=5)
    review_count: Optional[int] = Field(None, ge=0)
    shipping_info: Optional[str] = None
    seller_info: Optional[str] = None
    
    # Raw data
    raw_html: Optional[str] = None
    extracted_data: Dict[str, Any] = Field(default_factory=dict)
    
    # Quality metrics
    data_quality_score: Optional[float] = Field(None, ge=0, le=1)
    confidence_score: Optional[float] = Field(None, ge=0, le=1)
    
    # Scraping metadata
    scraped_at: datetime = Field(default_factory=datetime.utcnow, index=True)
    scraper_version: Optional[str] = None
    processing_time: Optional[float] = None  # seconds
    
    class Settings:
        name = "scraped_data"
        indexes = [
            [("competitor_id", 1), ("scraped_at", -1)],
            [("product_id", 1), ("scraped_at", -1)],
            "scrape_job_id",
            "scraped_at"
        ]

# Pydantic schemas for API
class ScrapeJobCreate(BaseModel):
    """Schema for creating scrape jobs"""
    job_type: JobType
    name: Optional[str] = None
    description: Optional[str] = None
    target_urls: List[str] = Field(default_factory=list)
    competitor_id: Optional[str] = None
    product_ids: List[str] = Field(default_factory=list)
    scraper_config: Dict[str, Any] = Field(default_factory=dict)
    priority: int = Field(default=0, ge=0)
    max_retries: int = Field(default=3, ge=0)

class ScrapeJobUpdate(BaseModel):
    """Schema for updating scrape jobs"""
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[JobStatus] = None
    priority: Optional[int] = Field(None, ge=0)

class ScrapeJobResponse(BaseModel):
    """Schema for scrape job responses"""
    id: str
    job_type: JobType
    name: Optional[str]
    status: JobStatus
    progress: float
    items_total: int
    items_scraped: int
    items_failed: int
    success_rate: float
    created_at: datetime
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    duration: Optional[int]
    competitor_name: Optional[str]
    error_summary: Dict[str, int]

class ScrapeRequest(BaseModel):
    """Schema for manual scrape requests"""
    urls: List[str] = Field(..., min_items=1)
    competitor_id: Optional[str] = None
    product_ids: Optional[List[str]] = None
    priority: int = Field(default=0, ge=0)
    config: Dict[str, Any] = Field(default_factory=dict)
