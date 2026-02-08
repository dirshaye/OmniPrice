from __future__ import annotations

from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

from omniprice.core.config import settings
from omniprice.core.exceptions import ValidationException

_TRACKING_PARAMS = {
    "utm_source",
    "utm_medium",
    "utm_campaign",
    "utm_term",
    "utm_content",
    "gclid",
    "fbclid",
    "srsltid",
    "ref",
    "v",
}


def _normalize_domain(netloc: str) -> str:
    host = netloc.lower().strip()
    if ":" in host:
        host = host.split(":", 1)[0]
    if host.startswith("www."):
        host = host[4:]
    return host


def extract_domain(url: str) -> str:
    return _normalize_domain(urlsplit(url).netloc)


def canonicalize_url(url: str) -> str:
    parts = urlsplit(url.strip())
    if not parts.scheme or not parts.netloc:
        raise ValidationException("Invalid product URL")

    scheme = parts.scheme.lower()
    netloc = _normalize_domain(parts.netloc)
    path = parts.path.rstrip("/") or "/"

    filtered_query = [
        (k, v)
        for k, v in parse_qsl(parts.query, keep_blank_values=False)
        if k.lower() not in _TRACKING_PARAMS
    ]
    query = urlencode(sorted(filtered_query), doseq=True)
    return urlunsplit((scheme, netloc, path, query, ""))


def is_domain_allowed(url: str) -> bool:
    if not settings.SCRAPER_ENFORCE_DOMAIN_ALLOWLIST:
        return True
    allowed = settings.SCRAPER_ALLOWED_DOMAINS
    if not allowed:
        return False

    domain = extract_domain(url)
    return any(domain == item or domain.endswith(f".{item}") for item in allowed)


def validate_scrape_url_allowed(url: str) -> None:
    if is_domain_allowed(url):
        return
    raise ValidationException(
        "URL domain is not allowed by scraper policy. "
        "Update SCRAPER_ALLOWED_DOMAINS or disable allowlist enforcement."
    )
