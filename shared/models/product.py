#!/usr/bin/env python3
"""
Enhanced Product models for OmniPriceX Product Service
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from enum import Enum
from beanie import Document, Indexed
from pydantic import Field, BaseModel
from bson import ObjectId

# Import base models
from .base import Product as BaseProduct, ProductStatus, PriceHistoryEntry


class CompetitorData(BaseModel):
    """Competitor pricing data"""
    competitor_name: str = Field(...)
    url: str = Field(...)
    price: Optional[float] = Field(None, ge=0)
    currency: str = Field(default="USD")
    last_scraped: Optional[datetime] = None
    is_available: bool = Field(default=True)
    scrape_errors: List[str] = Field(default_factory=list)


class EnhancedProduct(BaseProduct):
    """Enhanced Product document model for Product Service"""
    
    # Additional pricing fields
    min_price: Optional[float] = Field(None, ge=0)
    max_price: Optional[float] = Field(None, ge=0)
    cost_price: Optional[float] = Field(None, ge=0)
    currency: str = Field(default="USD")
    
    # Inventory fields
    stock_quantity: int = Field(default=0, ge=0)
    low_stock_threshold: int = Field(default=10, ge=0)
    
    # Status fields
    is_active: bool = Field(default=True)
    
    # Competitor tracking
    competitor_urls: Dict[str, str] = Field(default_factory=dict)
    competitor_data: List[CompetitorData] = Field(default_factory=list)
    
    # Additional metadata
    tags: List[str] = Field(default_factory=list)
    
    # Audit fields
    created_by: str = Field(...)
    
    # Indexes
    sku: Indexed(str, unique=True)  # type: ignore
    category: Indexed(str)  # type: ignore
    brand: Indexed(str)  # type: ignore
    status: Indexed(ProductStatus)  # type: ignore
    is_active: Indexed(bool)  # type: ignore
    
    class Settings:
        name = "products"
        indexes = [
            [("sku", 1)],  # Unique index on SKU
            [("category", 1)],
            [("brand", 1)],
            [("status", 1)],
            [("is_active", 1)],
            [("name", "text"), ("description", "text")],  # Text search index
            [("created_at", -1)],  # Sort by creation date
            [("updated_at", -1)],  # Sort by update date
        ]
    
    def __str__(self):
        return f"Product(name='{self.name}', sku='{self.sku}', price={self.current_price})"
    
    def __repr__(self):
        return self.__str__()
    
    @property
    def is_low_stock(self) -> bool:
        """Check if product is low on stock"""
        return self.stock_quantity <= self.low_stock_threshold
    
    @property
    def is_out_of_stock(self) -> bool:
        """Check if product is out of stock"""
        return self.stock_quantity == 0
    
    def add_price_history(self, new_price: float, changed_by: str, reason: Optional[str] = None):
        """Add price change to history"""
        if new_price != self.current_price:
            price_change = PriceHistoryEntry(
                price=new_price,
                timestamp=datetime.utcnow(),
                source=changed_by,
            )
            self.price_history.append(price_change)
            
            # Keep only the last 100 price changes
            if len(self.price_history) > 100:
                self.price_history = self.price_history[-100:]
            
            self.current_price = new_price
            self.updated_at = datetime.utcnow()
    
    def update_competitor_data(self, competitor_name: str, url: str, price: Optional[float] = None, 
                             is_available: bool = True, error: Optional[str] = None):
        """Update competitor pricing data"""
        # Find existing competitor data
        competitor_found = False
        for competitor in self.competitor_data:
            if competitor.competitor_name == competitor_name:
                competitor.price = price
                competitor.is_available = is_available
                competitor.last_scraped = datetime.utcnow()
                if error:
                    competitor.scrape_errors.append(error)
                    # Keep only last 5 errors
                    competitor.scrape_errors = competitor.scrape_errors[-5:]
                else:
                    competitor.scrape_errors = []
                competitor_found = True
                break
        
        # Add new competitor if not found
        if not competitor_found:
            new_competitor = CompetitorData(
                competitor_name=competitor_name,
                url=url,
                price=price,
                is_available=is_available,
                last_scraped=datetime.utcnow()
            )
            if error:
                new_competitor.scrape_errors.append(error)
            self.competitor_data.append(new_competitor)
        
        self.updated_at = datetime.utcnow()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API responses"""
        return {
            "id": str(self.id),
            "name": self.name,
            "sku": self.sku,
            "description": self.description,
            "category": self.category,
            "brand": self.brand,
            "base_price": self.base_price,
            "current_price": self.current_price,
            "min_price": self.min_price,
            "max_price": self.max_price,
            "cost_price": self.cost_price,
            "currency": self.currency,
            "stock_quantity": self.stock_quantity,
            "low_stock_threshold": self.low_stock_threshold,
            "status": self.status.value,
            "is_active": self.is_active,
            "competitor_urls": self.competitor_urls,
            "tags": self.tags,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "created_by": self.created_by,
            "is_low_stock": self.is_low_stock,
            "is_out_of_stock": self.is_out_of_stock
        }


# For backward compatibility, use the enhanced product as the main Product class
Product = EnhancedProduct
