from __future__ import annotations

import pytest

from omniprice.core.exceptions import ValidationException
from omniprice.integrations.scraper.url_policy import (
    canonicalize_url,
    extract_domain,
    is_domain_allowed,
    validate_scrape_url_allowed,
)


def test_canonicalize_url_removes_tracking_params_and_fragment():
    url = "https://www.MIGROS.com.tr/icim-rahat-laktozsuz-sut-1-l-p-a80012?utm_source=x&ref=foo&p=1#section"
    canonical = canonicalize_url(url)
    assert canonical == "https://migros.com.tr/icim-rahat-laktozsuz-sut-1-l-p-a80012?p=1"


def test_extract_domain_normalizes_www_and_port():
    assert extract_domain("https://www.sokmarket.com.tr:443/product") == "sokmarket.com.tr"


def test_is_domain_allowed_when_enforcement_disabled():
    assert is_domain_allowed("https://example.com/product") is True


def test_validate_scrape_url_allowed_when_enforced(monkeypatch):
    from omniprice.core.config import settings

    monkeypatch.setattr(settings, "SCRAPER_ENFORCE_DOMAIN_ALLOWLIST", True)
    monkeypatch.setattr(settings, "SCRAPER_ALLOWED_DOMAINS", ["migros.com.tr", "a101.com.tr"])

    validate_scrape_url_allowed("https://migros.com.tr/product/1")
    with pytest.raises(ValidationException):
        validate_scrape_url_allowed("https://example.com/product")
