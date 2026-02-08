from __future__ import annotations

from datetime import datetime
from typing import List

from omniprice.core.exceptions import ConflictException
from omniprice.core.exceptions import NotFoundException
from omniprice.integrations.scraper.url_policy import canonicalize_url, extract_domain, validate_scrape_url_allowed
from omniprice.models.competitor import Competitor, PriceHistory
from omniprice.repositories.competitor import CompetitorRepository, PriceHistoryRepository
from omniprice.schemas.competitor import CompetitorCreate, CompetitorUpdate, PriceHistoryCreate


class CompetitorService:
    @staticmethod
    async def list_competitors(limit: int = 50, offset: int = 0) -> List[Competitor]:
        return await CompetitorRepository.list(limit=limit, offset=offset)

    @staticmethod
    async def get_competitor(competitor_id: str) -> Competitor:
        competitor = await CompetitorRepository.get(competitor_id)
        if not competitor:
            raise NotFoundException("Competitor not found")
        return competitor

    @staticmethod
    async def create_competitor(payload: CompetitorCreate) -> Competitor:
        validate_scrape_url_allowed(payload.product_url)
        canonical_url = canonicalize_url(payload.product_url)
        existing = await CompetitorRepository.get_by_product_and_canonical_url(payload.product_id, canonical_url)
        if existing:
            raise ConflictException("Competitor URL is already tracked for this product")

        competitor = Competitor(
            **payload.model_dump(),
            product_url=canonical_url,
            canonical_url=canonical_url,
            domain=extract_domain(canonical_url),
        )
        return await CompetitorRepository.create(competitor)

    @staticmethod
    async def update_competitor(competitor_id: str, payload: CompetitorUpdate) -> Competitor:
        competitor = await CompetitorRepository.get(competitor_id)
        if not competitor:
            raise NotFoundException("Competitor not found")

        update_fields = payload.model_dump(exclude_unset=True)
        if "product_url" in update_fields:
            validate_scrape_url_allowed(update_fields["product_url"])
            canonical_url = canonicalize_url(update_fields["product_url"])
            existing = await CompetitorRepository.get_by_product_and_canonical_url(
                competitor.product_id,
                canonical_url,
            )
            if existing and str(existing.id) != str(competitor.id):
                raise ConflictException("Competitor URL is already tracked for this product")
            update_fields["product_url"] = canonical_url
            update_fields["canonical_url"] = canonical_url
            update_fields["domain"] = extract_domain(canonical_url)
        if update_fields:
            competitor = await CompetitorRepository.update(competitor, **update_fields)
        return competitor

    @staticmethod
    async def delete_competitor(competitor_id: str) -> None:
        competitor = await CompetitorRepository.get(competitor_id)
        if not competitor:
            raise NotFoundException("Competitor not found")
        await CompetitorRepository.delete(competitor)

    @staticmethod
    async def update_price_snapshot(
        competitor: Competitor,
        *,
        price: float,
        currency: str | None,
        source: str,
        confidence: float,
    ) -> Competitor:
        return await CompetitorRepository.update(
            competitor,
            last_price=price,
            last_currency=currency,
            last_source=source,
            last_confidence=confidence,
            last_checked_at=datetime.utcnow(),
        )

    @staticmethod
    async def record_price_history(payload: PriceHistoryCreate) -> PriceHistory:
        entry = PriceHistory(**payload.model_dump())
        return await PriceHistoryRepository.create(entry)

    @staticmethod
    async def list_price_history_by_product(product_id: str, limit: int = 100) -> List[PriceHistory]:
        return await PriceHistoryRepository.list_by_product(product_id, limit=limit)

    @staticmethod
    async def list_price_history_by_competitor(competitor_id: str, limit: int = 100) -> List[PriceHistory]:
        return await PriceHistoryRepository.list_by_competitor(competitor_id, limit=limit)
