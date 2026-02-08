from __future__ import annotations

from omniprice.core.cache import build_cache_key
from omniprice.services.analytics import _safe_percent_change


def test_build_cache_key_skips_empty_parts():
    key = build_cache_key("analytics", "dashboard", "", "  ", "tenant-1")
    assert key == "analytics:dashboard:tenant-1"


def test_safe_percent_change_with_zero_previous():
    assert _safe_percent_change(120.0, 0.0) == 0.0


def test_safe_percent_change_standard_case():
    assert _safe_percent_change(110.0, 100.0) == 10.0
