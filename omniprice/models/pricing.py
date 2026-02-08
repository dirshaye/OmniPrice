from __future__ import annotations

from datetime import datetime
from typing import Optional

from beanie import Document
from pydantic import Field


class PricingRule(Document):
    name: str
    description: Optional[str] = None
    type: str = "competitive"
    category: Optional[str] = None
    adjustment: float = 0.0
    status: str = "active"

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "pricing_rules"
