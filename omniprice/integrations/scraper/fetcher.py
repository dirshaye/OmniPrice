from __future__ import annotations

import asyncio
import json
import re
from dataclasses import dataclass
from typing import Optional
from urllib.parse import urlparse

import httpx
from bs4 import BeautifulSoup

from omniprice.core.config import settings
from omniprice.integrations.scraper.adapters import ExtractedPrice, get_adapter


@dataclass(frozen=True)
class FetchPriceResult:
    price: float
    currency: Optional[str]
    source: str
    confidence: float


_MONEY_WITH_CURRENCY_RE = re.compile(
    r"(?:(?P<cur1>₺|TL|TRY)\s*)?(?P<amount>\d{1,3}(?:[.,]\d{3})*(?:[.,]\d{2})|\d+(?:[.,]\d{2})?)(?:\s*(?P<cur2>₺|TL|TRY))?",
    flags=re.IGNORECASE,
)


def _to_float(amount: str) -> Optional[float]:
    s = amount.strip()
    if not s:
        return None
    if "," in s and "." in s:
        if s.rfind(",") > s.rfind("."):
            s = s.replace(".", "").replace(",", ".")
        else:
            s = s.replace(",", "")
    else:
        if "," in s and "." not in s:
            s = s.replace(".", "").replace(",", ".")
        else:
            s = s.replace(",", "")
    try:
        return float(s)
    except ValueError:
        return None


def _extract_json_ld_price(html: str) -> Optional[ExtractedPrice]:
    soup = BeautifulSoup(html, "html.parser")
    scripts = soup.find_all("script", attrs={"type": "application/ld+json"})
    for script in scripts:
        raw = (script.string or "").strip()
        if not raw:
            continue
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            continue

        candidates = data if isinstance(data, list) else [data]
        for item in candidates:
            if not isinstance(item, dict):
                continue
            offers = item.get("offers")
            if isinstance(offers, list):
                offers_list = offers
            elif isinstance(offers, dict):
                offers_list = [offers]
            else:
                offers_list = []
            for offer in offers_list:
                if not isinstance(offer, dict):
                    continue
                price = offer.get("price")
                currency = offer.get("priceCurrency")
                if price is None:
                    continue
                price_f = _to_float(str(price))
                if price_f is None:
                    continue
                return ExtractedPrice(
                    price=price_f,
                    currency=str(currency) if currency else None,
                    confidence=0.75,
                    reason="json-ld offers.price",
                )
    return None


def _extract_regex_price(html: str) -> Optional[ExtractedPrice]:
    m = _MONEY_WITH_CURRENCY_RE.search(html)
    if not m:
        return None
    price_f = _to_float(m.group("amount"))
    if price_f is None:
        return None
    if price_f <= 0:
        return None
    cur = m.group("cur1") or m.group("cur2")
    currency = "TRY" if cur else None
    return ExtractedPrice(price=price_f, currency=currency, confidence=0.35, reason="regex-with-currency")


async def _fetch_html_http(url: str) -> str:
    timeout = httpx.Timeout(settings.SCRAPER_TIMEOUT)
    headers = {"User-Agent": settings.SCRAPER_USER_AGENT, "Accept-Language": "tr-TR,tr;q=0.9,en;q=0.8"}
    async with httpx.AsyncClient(timeout=timeout, headers=headers, follow_redirects=True) as client:
        last_exc: Optional[Exception] = None
        for attempt in range(settings.SCRAPER_MAX_RETRIES):
            try:
                resp = await client.get(url)
                resp.raise_for_status()
                return resp.text
            except Exception as exc:
                last_exc = exc
                await asyncio.sleep(min(2**attempt, 5))
        raise last_exc or RuntimeError("Failed to fetch HTML")


async def _fetch_html_playwright(url: str) -> str:
    from playwright.async_api import async_playwright

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-dev-shm-usage"],
        )
        context = await browser.new_context(
            user_agent=settings.SCRAPER_USER_AGENT,
            locale="tr-TR",
        )
        page = await context.new_page()
        try:
            await page.goto(url, wait_until="networkidle", timeout=settings.SCRAPER_TIMEOUT * 1000)
            return await page.content()
        finally:
            await context.close()
            await browser.close()


def _extract_price_with_strategy(html: str, url: str) -> Optional[FetchPriceResult]:
    extracted = _extract_json_ld_price(html)
    if extracted:
        return FetchPriceResult(
            price=extracted.price,
            currency=extracted.currency,
            source="generic",
            confidence=extracted.confidence,
        )

    adapter = get_adapter(url)
    if adapter:
        extracted = adapter.extract(html)
        if extracted:
            host = urlparse(url).netloc
            return FetchPriceResult(
                price=extracted.price,
                currency=extracted.currency,
                source=f"adapter:{adapter.name}({host})",
                confidence=extracted.confidence,
            )

    extracted = _extract_regex_price(html)
    if extracted:
        return FetchPriceResult(
            price=extracted.price,
            currency=extracted.currency,
            source="generic-regex",
            confidence=extracted.confidence,
        )

    return None


async def fetch_price(url: str, *, allow_playwright_fallback: bool = True) -> FetchPriceResult:
    http_html = await _fetch_html_http(url)
    http_result = _extract_price_with_strategy(http_html, url)
    if http_result and not (
        allow_playwright_fallback and http_result.source == "generic-regex" and http_result.confidence < 0.5
    ):
        return http_result

    if not allow_playwright_fallback:
        if http_result:
            return http_result
        raise ValueError("No price found from HTTP fetch")

    rendered_html = await _fetch_html_playwright(url)
    rendered_result = _extract_price_with_strategy(rendered_html, url)
    if rendered_result:
        return FetchPriceResult(
            price=rendered_result.price,
            currency=rendered_result.currency,
            source=f"playwright->{rendered_result.source}",
            confidence=rendered_result.confidence,
        )

    raise ValueError("No price found after Playwright fallback")
