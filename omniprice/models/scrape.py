from __future__ import annotations

from datetime import datetime
from typing import Optional

from beanie import Document
from pydantic import Field


class ScrapeExecution(Document):
    url: str
    domain: str
    competitor_id: Optional[str] = None
    product_id: Optional[str] = None

    status: str  # success | retry_scheduled | failed_permanent | failed_transient | invalid_payload
    error_class: Optional[str] = None
    error_message: Optional[str] = None

    source: Optional[str] = None
    confidence: Optional[float] = None
    price: Optional[float] = None
    currency: Optional[str] = None
    used_playwright: bool = False

    attempt: int = 0
    latency_ms: Optional[int] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "scrape_executions"
        indexes = [
            [("domain", 1), ("created_at", -1)],
            [("status", 1), ("created_at", -1)],
        ]
