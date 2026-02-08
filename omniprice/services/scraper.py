from __future__ import annotations

from datetime import datetime

from omniprice.core.config import settings
from omniprice.integrations.scraper.url_policy import canonicalize_url, extract_domain, validate_scrape_url_allowed
from omniprice.core.queue import publish_json_message
from omniprice.integrations.scraper.fetcher import FetchPriceResult, fetch_price


class ScraperService:
    @staticmethod
    async def fetch_price(url: str, *, allow_playwright_fallback: bool = True) -> FetchPriceResult:
        validate_scrape_url_allowed(url)
        canonical_url = canonicalize_url(url)
        return await fetch_price(canonical_url, allow_playwright_fallback=allow_playwright_fallback)

    @staticmethod
    async def enqueue_scrape(
        *,
        url: str,
        competitor_id: str | None = None,
        product_id: str | None = None,
        requested_by: str = "api",
    ) -> dict:
        validate_scrape_url_allowed(url)
        canonical_url = canonicalize_url(url)
        payload = {
            "url": canonical_url,
            "domain": extract_domain(canonical_url),
            "competitor_id": competitor_id,
            "product_id": product_id,
            "requested_by": requested_by,
            "requested_at": datetime.utcnow().isoformat() + "Z",
        }
        await publish_json_message(
            queue_name=settings.RABBITMQ_QUEUE_SCRAPE,
            payload=payload,
        )
        return {
            "queued": True,
            "queue": settings.RABBITMQ_QUEUE_SCRAPE,
            "payload": payload,
        }
