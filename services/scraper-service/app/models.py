"""
Database models for scraper service
"""

from datetime import datetime
from enum import Enum
from typing import Dict, Any, Optional, List
from beanie import Document
from pydantic import BaseModel, Field
from beanie import PydanticObjectId

class ScrapeJobStatus(str, Enum):
    """Status enum for scrape jobs"""
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"

class ScrapeJob(Document):
    """Scrape job document"""
    
    job_id: str = Field(default_factory=lambda: str(PydanticObjectId()))
    url: str
    status: ScrapeJobStatus = ScrapeJobStatus.PENDING
    priority: int = Field(default=5, ge=1, le=10)  # 1 = highest priority
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    # Results and metadata
    result: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    retry_count: int = 0
    
    # Configuration
    config: Dict[str, Any] = Field(default_factory=dict)
    
    class Settings:
        name = "scrape_jobs"
        indexes = [
            "status",
            "created_at",
            "priority",
            ("url", "status"),
        ]

class ScrapedProduct(BaseModel):
    """Scraped product data model"""
    
    # Basic info
    title: Optional[str] = None
    price: Optional[float] = None
    currency: str = "USD"
    original_price: Optional[float] = None
    availability: str = "unknown"
    
    # Additional data
    brand: Optional[str] = None
    description: Optional[str] = None
    image_urls: List[str] = Field(default_factory=list)
    rating: Optional[float] = None
    review_count: Optional[int] = None
    
    # Metadata
    source_url: str
    scraped_at: datetime = Field(default_factory=datetime.utcnow)
    raw_data: Dict[str, Any] = Field(default_factory=dict)

class ScrapeHistory(Document):
    """Historical scrape data"""
    
    url: str
    scraped_data: Dict[str, Any]
    scraped_at: datetime = Field(default_factory=datetime.utcnow)
    job_id: Optional[str] = None
    
    class Settings:
        name = "scrape_history"
        indexes = [
            "url",
            "scraped_at",
            ("url", "scraped_at"),
        ]
