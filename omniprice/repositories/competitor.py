from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from omniprice.models.competitor import Competitor, PriceHistory


class CompetitorRepository:
    @staticmethod
    async def list(limit: int = 50, offset: int = 0) -> List[Competitor]:
        return await Competitor.find().skip(offset).limit(limit).to_list()

    @staticmethod
    async def get(competitor_id: str) -> Optional[Competitor]:
        return await Competitor.get(competitor_id)

    @staticmethod
    async def create(competitor: Competitor) -> Competitor:
        return await competitor.insert()

    @staticmethod
    async def get_by_product_and_canonical_url(
        product_id: str,
        canonical_url: str,
    ) -> Optional[Competitor]:
        return await Competitor.find_one(
            (Competitor.product_id == product_id) & (Competitor.canonical_url == canonical_url)
        )

    @staticmethod
    async def update(competitor: Competitor, **fields) -> Competitor:
        fields["updated_at"] = datetime.utcnow()
        await competitor.set(fields)
        return competitor

    @staticmethod
    async def delete(competitor: Competitor) -> None:
        await competitor.delete()

    @staticmethod
    async def list_active() -> List[Competitor]:
        return await Competitor.find(Competitor.is_active == True).to_list()


class PriceHistoryRepository:
    @staticmethod
    async def create(entry: PriceHistory) -> PriceHistory:
        return await entry.insert()

    @staticmethod
    async def list_by_product(product_id: str, limit: int = 100) -> List[PriceHistory]:
        return await PriceHistory.find(PriceHistory.product_id == product_id).sort("-captured_at").limit(limit).to_list()

    @staticmethod
    async def list_by_competitor(competitor_id: str, limit: int = 100) -> List[PriceHistory]:
        return await PriceHistory.find(PriceHistory.competitor_id == competitor_id).sort("-captured_at").limit(limit).to_list()

    @staticmethod
    async def latest_for_competitor(competitor_id: str) -> Optional[PriceHistory]:
        return await PriceHistory.find(PriceHistory.competitor_id == competitor_id).sort("-captured_at").first_or_none()
