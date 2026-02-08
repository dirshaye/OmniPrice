from fastapi import APIRouter, Depends, HTTPException, status
from omniprice.core.cache import build_cache_key, cache_get_json, cache_set_json
from omniprice.core.ratelimit import rate_limit_dependency
from omniprice.integrations.scraper.url_policy import canonicalize_url
from omniprice.schemas.scraper import (
    ScrapeEnqueueRequest,
    ScrapeEnqueueResponse,
    ScrapeRequest,
    ScrapeResponse,
)

from omniprice.services.scraper import ScraperService

router = APIRouter()


@router.post(
    "/fetch",
    response_model=ScrapeResponse,
    dependencies=[Depends(rate_limit_dependency(namespace="scraper_fetch", max_requests=12, window_seconds=60))],
)
async def fetch_price(payload: ScrapeRequest):
    competitor = None
    product_id = payload.product_id
    canonical_url = canonicalize_url(str(payload.url))
    cache_key = build_cache_key("scrape", canonical_url)

    cached = await cache_get_json(cache_key)
    if cached:
        return ScrapeResponse(**cached)

    if payload.competitor_id:
        from omniprice.services.competitor import CompetitorService

        competitor = await CompetitorService.get_competitor(payload.competitor_id)
        if not product_id:
            product_id = competitor.product_id

    try:
        result = await ScraperService.fetch_price(
            canonical_url,
            allow_playwright_fallback=payload.allow_playwright_fallback,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=f"Scraper provider error: {exc}") from exc

    if competitor or product_id:
        from omniprice.schemas.competitor import PriceHistoryCreate
        from omniprice.services.competitor import CompetitorService

        if competitor:
            await CompetitorService.update_price_snapshot(
                competitor,
                price=result.price,
                currency=result.currency,
                source=result.source,
                confidence=result.confidence,
            )
        if product_id:
            await CompetitorService.record_price_history(
                PriceHistoryCreate(
                    product_id=product_id,
                    competitor_id=str(competitor.id) if competitor else None,
                    source_url=canonical_url,
                    price=result.price,
                    currency=result.currency,
                    source=result.source,
                    confidence=result.confidence,
                )
            )

    response = ScrapeResponse(
        price=result.price,
        currency=result.currency,
        source=result.source,
        confidence=result.confidence,
    )
    await cache_set_json(cache_key, response.model_dump(), ttl_seconds=900)
    return response


@router.post(
    "/enqueue",
    response_model=ScrapeEnqueueResponse,
    status_code=status.HTTP_202_ACCEPTED,
    dependencies=[Depends(rate_limit_dependency(namespace="scraper_enqueue", max_requests=20, window_seconds=60))],
)
async def enqueue_scrape(payload: ScrapeEnqueueRequest):
    result = await ScraperService.enqueue_scrape(
        url=str(payload.url),
        competitor_id=payload.competitor_id,
        product_id=payload.product_id,
    )
    return ScrapeEnqueueResponse(**result)
