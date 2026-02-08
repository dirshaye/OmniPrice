from __future__ import annotations

import os

import httpx
import pytest

os.environ["DEBUG"] = "false"

import omniprice.main as main_module
from omniprice.core.security import create_access_token
from omniprice.main import app
from omniprice.services.llm import LLMService
from omniprice.services.scraper import ScraperService


@pytest.mark.asyncio
async def test_llm_provider_error_returns_502(monkeypatch):
    auth_headers = {"Authorization": f"Bearer {create_access_token({'sub': 'integration@test.local'})}"}
    async def _noop_init_db():
        return None

    def _broken_ask(prompt: str, context: str | None = None, *, model_name: str = "gemini-flash-latest"):
        raise RuntimeError("provider unavailable")

    monkeypatch.setattr(main_module, "init_db", _noop_init_db)
    monkeypatch.setattr(LLMService, "ask", staticmethod(_broken_ask))

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        response = await client.post(
            "/api/v1/llm/ask",
            json={"prompt": "hello gemini", "context": "test", "model": "gemini-1.5-flash"},
            headers=auth_headers,
        )

    assert response.status_code == 502
    assert response.json()["detail"] == "LLM provider error. Check model name and API key."


@pytest.mark.asyncio
async def test_scraper_not_found_price_returns_422(monkeypatch):
    auth_headers = {"Authorization": f"Bearer {create_access_token({'sub': 'integration@test.local'})}"}
    async def _noop_init_db():
        return None

    async def _no_price(url: str, *, allow_playwright_fallback: bool = True):
        raise ValueError("No price found after Playwright fallback")

    monkeypatch.setattr(main_module, "init_db", _noop_init_db)
    monkeypatch.setattr(ScraperService, "fetch_price", staticmethod(_no_price))

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        response = await client.post(
            "/api/v1/scraper/fetch",
            json={"url": "https://example.com/no-price"},
            headers=auth_headers,
        )

    assert response.status_code == 422
    assert "No price found" in response.json()["detail"]


@pytest.mark.asyncio
async def test_scraper_provider_error_returns_502(monkeypatch):
    auth_headers = {"Authorization": f"Bearer {create_access_token({'sub': 'integration@test.local'})}"}
    async def _noop_init_db():
        return None

    async def _broken_fetch(url: str, *, allow_playwright_fallback: bool = True):
        raise RuntimeError("target temporarily blocked")

    monkeypatch.setattr(main_module, "init_db", _noop_init_db)
    monkeypatch.setattr(ScraperService, "fetch_price", staticmethod(_broken_fetch))

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        response = await client.post(
            "/api/v1/scraper/fetch",
            json={"url": "https://example.com/error"},
            headers=auth_headers,
        )

    assert response.status_code == 502
    assert "Scraper provider error" in response.json()["detail"]
