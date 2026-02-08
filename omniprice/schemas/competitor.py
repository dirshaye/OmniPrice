from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class CompetitorCreate(BaseModel):
    product_id: str
    competitor_name: str = Field(min_length=1)
    product_url: str = Field(min_length=5)
    is_active: bool = True


class CompetitorUpdate(BaseModel):
    competitor_name: Optional[str] = None
    product_url: Optional[str] = None
    is_active: Optional[bool] = None


class CompetitorResponse(BaseModel):
    id: str
    product_id: str
    competitor_name: str
    product_url: str
    canonical_url: Optional[str] = None
    domain: Optional[str] = None
    is_active: bool
    last_price: Optional[float]
    last_currency: Optional[str]
    last_source: Optional[str]
    last_confidence: Optional[float]
    last_checked_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime


class PriceHistoryCreate(BaseModel):
    product_id: str
    competitor_id: Optional[str] = None
    source_url: Optional[str] = None
    price: float
    currency: Optional[str] = None
    source: str
    confidence: float


class PriceHistoryResponse(BaseModel):
    id: str
    product_id: str
    competitor_id: Optional[str] = None
    source_url: Optional[str] = None
    price: float
    currency: Optional[str] = None
    source: str
    confidence: float
    captured_at: datetime
