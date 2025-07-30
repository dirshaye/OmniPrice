from beanie import Document
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class User(Document):
    # Simplified User model for product service context
    id: str
    username: str
    email: str

    class Settings:
        name = "users"

class Price(BaseModel):
    value: float
    currency: str
    timestamp: datetime = datetime.now()

class Product(Document):
    name: str
    description: Optional[str] = None
    sku: str
    barcode: Optional[str] = None
    brand: Optional[str] = None
    category: str
    price_history: List[Price] = []
    current_price: Price
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()

    class Settings:
        name = "products"

class ProductCompetitor(Document):
    product_id: str
    competitor_id: str
    competitor_product_url: str
    price_history: List[Price] = []
    current_price: Price
    last_scraped: datetime

    class Settings:
        name = "product_competitors"
