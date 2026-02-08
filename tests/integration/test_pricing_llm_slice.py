from __future__ import annotations

import os

import httpx
import pytest

# Keep tests deterministic even if local .env contains incompatible DEBUG value.
os.environ["DEBUG"] = "false"

import omniprice.main as main_module
from omniprice.core.security import create_access_token
from omniprice.main import app
from omniprice.services.llm import LLMService
from omniprice.services.pricing import PricingService


@pytest.mark.asyncio
async def test_pricing_recommendation_endpoint_slice(monkeypatch):
    auth_headers = {"Authorization": f"Bearer {create_access_token({'sub': 'integration@test.local'})}"}
    async def _noop_init_db():
        return None

    called: dict[str, str] = {}

    async def _recommend_price(product_id: str):
        called["product_id"] = product_id
        return {
            "product_id": product_id,
            "current_price": 100.0,
            "suggested_price": 96.5,
            "reason": "Competitive rule: -3.5% vs competitor average",
        }

    monkeypatch.setattr(main_module, "init_db", _noop_init_db)
    monkeypatch.setattr(PricingService, "recommend_price", staticmethod(_recommend_price))

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        response = await client.get("/api/v1/pricing/recommendations/prod-123", headers=auth_headers)

    assert response.status_code == 200
    payload = response.json()
    assert payload["product_id"] == "prod-123"
    assert payload["current_price"] == 100.0
    assert payload["suggested_price"] == 96.5
    assert "Competitive rule" in payload["reason"]
    assert called["product_id"] == "prod-123"


@pytest.mark.asyncio
async def test_llm_ask_endpoint_slice(monkeypatch):
    auth_headers = {"Authorization": f"Bearer {create_access_token({'sub': 'integration@test.local'})}"}
    async def _noop_init_db():
        return None

    called: dict[str, str | None] = {}

    def _ask(prompt: str, context: str | None = None, *, model_name: str = "gemini-flash-latest") -> str:
        called["prompt"] = prompt
        called["context"] = context
        called["model_name"] = model_name
        return "Suggested price: TRY 96.5 because competitor average is lower."

    monkeypatch.setattr(main_module, "init_db", _noop_init_db)
    monkeypatch.setattr(LLMService, "ask", staticmethod(_ask))

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        response = await client.post(
            "/api/v1/llm/ask",
            json={
                "prompt": "What price should we set for product X?",
                "context": "Current price 100, competitor average 97",
                "model": "gemini-1.5-flash",
            },
            headers=auth_headers,
        )

    assert response.status_code == 200
    assert response.json()["response"].startswith("Suggested price:")
    assert called["prompt"] == "What price should we set for product X?"
    assert called["context"] == "Current price 100, competitor average 97"
    assert called["model_name"] == "gemini-1.5-flash"
