from __future__ import annotations

from datetime import datetime
from typing import Optional

from beanie import Document
from pydantic import Field


class Product(Document):
    name: str
    sku: Optional[str] = None
    category: Optional[str] = None
    cost: Optional[float] = None
    current_price: float
    stock_quantity: Optional[int] = None
    is_active: bool = True

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "products"
