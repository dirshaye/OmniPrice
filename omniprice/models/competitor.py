from __future__ import annotations

from datetime import datetime
from typing import Optional

from beanie import Document
from pydantic import Field


class Competitor(Document):
    product_id: str
    competitor_name: str
    product_url: str
    canonical_url: Optional[str] = None
    domain: Optional[str] = None
    is_active: bool = True

    last_price: Optional[float] = None
    last_currency: Optional[str] = None
    last_source: Optional[str] = None
    last_confidence: Optional[float] = None
    last_checked_at: Optional[datetime] = None

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "competitors"
        indexes = [
            [("product_id", 1), ("canonical_url", 1)],
        ]


class PriceHistory(Document):
    product_id: str
    competitor_id: Optional[str] = None
    source_url: Optional[str] = None
    price: float
    currency: Optional[str] = None
    source: str
    confidence: float
    captured_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "price_history"
