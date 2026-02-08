from pydantic import AnyUrl, BaseModel, Field


class ScrapeRequest(BaseModel):
    url: AnyUrl
    allow_playwright_fallback: bool = Field(default=True)
    competitor_id: str | None = None
    product_id: str | None = None


class ScrapeResponse(BaseModel):
    price: float
    currency: str | None
    source: str
    confidence: float


class ScrapeEnqueueRequest(BaseModel):
    url: AnyUrl
    competitor_id: str | None = None
    product_id: str | None = None


class ScrapeEnqueueResponse(BaseModel):
    queued: bool
    queue: str
    payload: dict
