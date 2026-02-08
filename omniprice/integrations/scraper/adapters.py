from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Optional
from urllib.parse import urlparse

from bs4 import BeautifulSoup


@dataclass(frozen=True)
class ExtractedPrice:
    price: float
    currency: Optional[str]
    confidence: float
    reason: str


class SiteAdapter:
    name: str

    def matches(self, url: str) -> bool:  # pragma: no cover
        raise NotImplementedError

    def extract(self, html: str) -> Optional[ExtractedPrice]:  # pragma: no cover
        raise NotImplementedError


def _parse_price_text(text: str) -> Optional[tuple[float, Optional[str]]]:
    s = " ".join(text.split()).strip()
    if not s:
        return None

    m = re.search(r"(?:₺|TL|TRY)?\s*([0-9][0-9.,]*)\s*(?:TL|TRY)?", s, flags=re.IGNORECASE)
    if not m:
        return None

    amount_raw = m.group(1)
    try:
        amount = float(amount_raw.replace(".", "").replace(",", "."))
    except ValueError:
        return None

    currency = "TRY" if re.search(r"(₺|TL|TRY)", s, flags=re.IGNORECASE) else None
    return amount, currency


def _extract_from_meta(html: str) -> Optional[ExtractedPrice]:
    soup = BeautifulSoup(html, "html.parser")
    meta_candidates = [
        ("property", "product:price:amount"),
        ("property", "og:price:amount"),
        ("name", "price"),
        ("itemprop", "price"),
    ]
    for attr, key in meta_candidates:
        tag = soup.find("meta", attrs={attr: key})
        if not tag:
            continue
        content = tag.get("content")
        if not content:
            continue
        try:
            price = float(str(content).replace(",", "."))
        except ValueError:
            continue
        currency_tag = soup.find("meta", attrs={"property": "product:price:currency"})
        currency = currency_tag.get("content") if currency_tag else None
        return ExtractedPrice(price=price, currency=currency, confidence=0.65, reason="meta price")
    return None


def _extract_from_next_data(html: str) -> Optional[dict]:
    soup = BeautifulSoup(html, "html.parser")
    tag = soup.find("script", attrs={"id": "__NEXT_DATA__"})
    if not tag or not tag.string:
        return None
    try:
        return json.loads(tag.string)
    except json.JSONDecodeError:
        return None


def _deep_find_first_number(obj) -> Optional[float]:
    if isinstance(obj, (int, float)) and obj > 0:
        return float(obj)
    if isinstance(obj, str):
        try:
            v = float(obj.replace(",", "."))
            if v > 0:
                return v
        except ValueError:
            return None
    if isinstance(obj, list):
        for item in obj:
            v = _deep_find_first_number(item)
            if v is not None:
                return v
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k.lower() in {"price", "currentprice", "saleprice", "finalprice", "amount"}:
                n = _deep_find_first_number(v)
                if n is not None:
                    return n
            n = _deep_find_first_number(v)
            if n is not None:
                return n
    return None


class MigrosAdapter(SiteAdapter):
    name = "migros"

    def matches(self, url: str) -> bool:
        return "migros.com.tr" in urlparse(url).netloc

    def extract(self, html: str) -> Optional[ExtractedPrice]:
        soup = BeautifulSoup(html, "html.parser")

        pdp = soup.find("sm-product-detail-page")
        if pdp:
            price_tag = pdp.find("fe-product-price")
            if price_tag:
                parsed = _parse_price_text(" ".join(price_tag.stripped_strings))
                if parsed:
                    amount, currency = parsed
                    return ExtractedPrice(price=amount, currency=currency, confidence=0.8, reason="pdp fe-product-price")

        meta = _extract_from_meta(html)
        if meta:
            return meta
        data = _extract_from_next_data(html)
        if data:
            price = _deep_find_first_number(data)
            if price is not None:
                return ExtractedPrice(price=price, currency="TRY", confidence=0.55, reason="next-data heuristic")
        return None


class A101Adapter(SiteAdapter):
    name = "a101"

    def matches(self, url: str) -> bool:
        return "a101.com.tr" in urlparse(url).netloc

    def extract(self, html: str) -> Optional[ExtractedPrice]:
        meta = _extract_from_meta(html)
        if meta:
            return meta
        data = _extract_from_next_data(html)
        if not data:
            return None
        price = _deep_find_first_number(data)
        if price is None:
            return None
        return ExtractedPrice(price=price, currency="TRY", confidence=0.55, reason="next-data heuristic")


class SokAdapter(SiteAdapter):
    name = "sok"

    def matches(self, url: str) -> bool:
        return "sokmarket.com.tr" in urlparse(url).netloc

    def extract(self, html: str) -> Optional[ExtractedPrice]:
        meta = _extract_from_meta(html)
        if meta:
            return meta
        data = _extract_from_next_data(html)
        if not data:
            return None
        price = _deep_find_first_number(data)
        if price is None:
            return None
        return ExtractedPrice(price=price, currency="TRY", confidence=0.55, reason="next-data heuristic")


class GetirAdapter(SiteAdapter):
    name = "getir"

    def matches(self, url: str) -> bool:
        return "getir.com" in urlparse(url).netloc

    def extract(self, html: str) -> Optional[ExtractedPrice]:
        return _extract_from_meta(html)


_ADAPTERS: list[SiteAdapter] = [MigrosAdapter(), A101Adapter(), SokAdapter(), GetirAdapter()]


def get_adapter(url: str) -> Optional[SiteAdapter]:
    for adapter in _ADAPTERS:
        if adapter.matches(url):
            return adapter
    return None
