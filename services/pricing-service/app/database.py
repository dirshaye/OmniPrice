from beanie import Document
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class PricingRule(Document):
    name: str
    description: Optional[str] = None
    conditions: dict
    actions: dict
    is_active: bool = True
    priority: int = 0
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()

    class Settings:
        name = "pricing_rules"
