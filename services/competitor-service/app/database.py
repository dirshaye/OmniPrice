from beanie import Document
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class Competitor(Document):
    name: str
    domain: str
    website_url: str
    description: Optional[str] = None
    status: str = "active"
    is_active: bool = True
    scraping_enabled: bool = True
    scraping_frequency: int = 60 # in minutes
    last_scraped: Optional[datetime] = None
    last_successful_scrape: Optional[datetime] = None
    consecutive_failures: int = 0
    success_rate: float = 1.0
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()

    class Settings:
        name = "competitors"

class CompetitorProduct(Document):
    competitor_id: str
    product_url: str
    current_price: float
    original_price: Optional[float] = None
    availability: str
    last_updated: datetime
    currency: str
    title: str
    image_url: Optional[str] = None
    rating: Optional[float] = None
    review_count: Optional[int] = None

    class Settings:
        name = "competitor_products"
