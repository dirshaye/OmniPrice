from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class ProductCreate(BaseModel):
    name: str = Field(min_length=1)
    sku: Optional[str] = None
    category: Optional[str] = None
    cost: Optional[float] = None
    current_price: float = Field(gt=0)
    stock_quantity: Optional[int] = Field(default=None, ge=0)
    is_active: bool = True


class ProductUpdate(BaseModel):
    name: Optional[str] = None
    sku: Optional[str] = None
    category: Optional[str] = None
    cost: Optional[float] = None
    current_price: Optional[float] = Field(default=None, gt=0)
    stock_quantity: Optional[int] = Field(default=None, ge=0)
    is_active: Optional[bool] = None


class ProductResponse(BaseModel):
    id: str
    name: str
    sku: Optional[str]
    category: Optional[str]
    cost: Optional[float]
    current_price: float
    stock_quantity: Optional[int]
    is_active: bool
    created_at: datetime
    updated_at: datetime
