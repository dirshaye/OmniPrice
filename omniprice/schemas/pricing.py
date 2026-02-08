from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class PricingRuleCreate(BaseModel):
    name: str = Field(min_length=1)
    description: Optional[str] = None
    type: str = "competitive"
    category: Optional[str] = None
    adjustment: float = 0.0
    status: str = "active"


class PricingRuleUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    type: Optional[str] = None
    category: Optional[str] = None
    adjustment: Optional[float] = None
    status: Optional[str] = None


class PricingRuleResponse(BaseModel):
    id: str
    name: str
    description: Optional[str]
    type: str
    category: Optional[str]
    adjustment: float
    status: str
    created_at: datetime
    updated_at: datetime


class PricingRecommendationResponse(BaseModel):
    product_id: str
    current_price: Optional[float]
    suggested_price: Optional[float]
    reason: str
