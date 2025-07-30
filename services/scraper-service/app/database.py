from beanie import Document
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class ScrapeJob(Document):
    url: str
    status: str
    priority: int
    scraped_data: Optional[dict] = None
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()

    class Settings:
        name = "scrape_jobs"
