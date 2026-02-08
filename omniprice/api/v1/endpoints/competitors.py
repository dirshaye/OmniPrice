import logging

from fastapi import APIRouter, status

from omniprice.schemas.competitor import CompetitorCreate, CompetitorResponse, CompetitorUpdate
from omniprice.services.competitor import CompetitorService
from omniprice.services.scraper import ScraperService

router = APIRouter()
logger = logging.getLogger(__name__)


def _to_response(c) -> CompetitorResponse:
    return CompetitorResponse(
        id=str(c.id),
        product_id=c.product_id,
        competitor_name=c.competitor_name,
        product_url=c.product_url,
        canonical_url=getattr(c, "canonical_url", None),
        domain=getattr(c, "domain", None),
        is_active=c.is_active,
        last_price=c.last_price,
        last_currency=c.last_currency,
        last_source=c.last_source,
        last_confidence=c.last_confidence,
        last_checked_at=c.last_checked_at,
        created_at=c.created_at,
        updated_at=c.updated_at,
    )


@router.get("/", response_model=list[CompetitorResponse])
async def list_competitors(limit: int = 50, offset: int = 0):
    competitors = await CompetitorService.list_competitors(limit=limit, offset=offset)
    return [_to_response(c) for c in competitors]


@router.post("/", response_model=CompetitorResponse, status_code=status.HTTP_201_CREATED)
async def create_competitor(payload: CompetitorCreate, enqueue_scrape: bool = True):
    competitor = await CompetitorService.create_competitor(payload)
    if enqueue_scrape:
        try:
            await ScraperService.enqueue_scrape(
                url=competitor.product_url,
                competitor_id=str(competitor.id),
                product_id=competitor.product_id,
                requested_by="competitor_create",
            )
        except Exception as exc:
            logger.warning("Failed to enqueue initial scrape for competitor %s: %s", competitor.id, exc)
    return _to_response(competitor)


@router.get("/{competitor_id}", response_model=CompetitorResponse)
async def get_competitor(competitor_id: str):
    return _to_response(await CompetitorService.get_competitor(competitor_id))


@router.put("/{competitor_id}", response_model=CompetitorResponse)
async def update_competitor(competitor_id: str, payload: CompetitorUpdate):
    return _to_response(await CompetitorService.update_competitor(competitor_id, payload))


@router.delete("/{competitor_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_competitor(competitor_id: str):
    await CompetitorService.delete_competitor(competitor_id)
    return None
