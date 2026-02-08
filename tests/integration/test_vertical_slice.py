from __future__ import annotations

import os
from datetime import datetime
from types import SimpleNamespace

import httpx
import pytest

# Make test deterministic even if local .env contains non-boolean DEBUG values.
os.environ["DEBUG"] = "false"

import omniprice.main as main_module
from omniprice.core.security import create_access_token
from omniprice.integrations.scraper.fetcher import FetchPriceResult
from omniprice.main import app
from omniprice.services.competitor import CompetitorService
from omniprice.services.product import ProductService
from omniprice.services.scraper import ScraperService


@pytest.mark.asyncio
async def test_product_competitor_scraper_price_history_vertical_slice(monkeypatch):
    auth_headers = {"Authorization": f"Bearer {create_access_token({'sub': 'integration@test.local'})}"}
    products: dict[str, SimpleNamespace] = {}
    competitors: dict[str, SimpleNamespace] = {}
    price_history: list[SimpleNamespace] = []

    async def _noop_init_db():
        return None

    async def _create_product(payload):
        product_id = f"p{len(products) + 1}"
        now = datetime.utcnow()
        obj = SimpleNamespace(
            id=product_id,
            name=payload.name,
            sku=payload.sku,
            category=payload.category,
            cost=payload.cost,
            current_price=payload.current_price,
            stock_quantity=payload.stock_quantity,
            is_active=payload.is_active,
            created_at=now,
            updated_at=now,
        )
        products[product_id] = obj
        return obj

    async def _create_competitor(payload):
        competitor_id = f"c{len(competitors) + 1}"
        now = datetime.utcnow()
        obj = SimpleNamespace(
            id=competitor_id,
            product_id=payload.product_id,
            competitor_name=payload.competitor_name,
            product_url=payload.product_url,
            is_active=payload.is_active,
            last_price=None,
            last_currency=None,
            last_source=None,
            last_confidence=None,
            last_checked_at=None,
            created_at=now,
            updated_at=now,
        )
        competitors[competitor_id] = obj
        return obj

    async def _get_competitor(competitor_id: str):
        return competitors[competitor_id]

    async def _update_price_snapshot(competitor, *, price, currency, source, confidence):
        competitor.last_price = price
        competitor.last_currency = currency
        competitor.last_source = source
        competitor.last_confidence = confidence
        competitor.last_checked_at = datetime.utcnow()
        competitor.updated_at = datetime.utcnow()
        return competitor

    async def _record_price_history(payload):
        entry = SimpleNamespace(
            id=f"h{len(price_history) + 1}",
            product_id=payload.product_id,
            competitor_id=payload.competitor_id,
            source_url=payload.source_url,
            price=payload.price,
            currency=payload.currency,
            source=payload.source,
            confidence=payload.confidence,
            captured_at=datetime.utcnow(),
        )
        price_history.append(entry)
        return entry

    async def _fetch_price(_url: str, *, allow_playwright_fallback: bool = True):
        assert allow_playwright_fallback is True
        return FetchPriceResult(price=42.5, currency="TRY", source="adapter:test", confidence=0.9)

    monkeypatch.setattr(main_module, "init_db", _noop_init_db)
    monkeypatch.setattr(ProductService, "create_product", staticmethod(_create_product))
    monkeypatch.setattr(CompetitorService, "create_competitor", staticmethod(_create_competitor))
    monkeypatch.setattr(CompetitorService, "get_competitor", staticmethod(_get_competitor))
    monkeypatch.setattr(CompetitorService, "update_price_snapshot", staticmethod(_update_price_snapshot))
    monkeypatch.setattr(CompetitorService, "record_price_history", staticmethod(_record_price_history))
    monkeypatch.setattr(ScraperService, "fetch_price", staticmethod(_fetch_price))

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        product_resp = await client.post(
            "/api/v1/products/",
            json={
                "name": "Milk 1L",
                "sku": "MLK-1L",
                "category": "grocery",
                "cost": 25.0,
                "current_price": 30.0,
                "stock_quantity": 10,
                "is_active": True,
            },
            headers=auth_headers,
        )
        assert product_resp.status_code == 201
        product_id = product_resp.json()["id"]

        competitor_resp = await client.post(
            "/api/v1/competitors/",
            json={
                "product_id": product_id,
                "competitor_name": "A101",
                "product_url": "https://example.com/a101/milk-1l",
                "is_active": True,
            },
            headers=auth_headers,
        )
        assert competitor_resp.status_code == 201
        competitor_id = competitor_resp.json()["id"]

        scrape_resp = await client.post(
            "/api/v1/scraper/fetch",
            json={
                "url": "https://example.com/a101/milk-1l",
                "competitor_id": competitor_id,
                "allow_playwright_fallback": True,
            },
            headers=auth_headers,
        )
        assert scrape_resp.status_code == 200
        data = scrape_resp.json()
        assert data["price"] == 42.5
        assert data["currency"] == "TRY"
        assert data["source"] == "adapter:test"

    assert competitors[competitor_id].last_price == 42.5
    assert competitors[competitor_id].last_currency == "TRY"
    assert len(price_history) == 1
    assert price_history[0].product_id == product_id
    assert price_history[0].competitor_id == competitor_id
