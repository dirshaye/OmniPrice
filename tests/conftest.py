"""Shared pytest fixtures for OmniPrice tests."""

from __future__ import annotations

import os

import pytest

# Keep test startup deterministic even when local .env has non-boolean debug values.
os.environ.setdefault("DEBUG", "false")


@pytest.fixture
def auth_headers():
    """Return a valid JWT Authorization header for protected endpoint tests."""
    from omniprice.core.security import create_access_token

    token = create_access_token({"sub": "tests@omniprice.local"})
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture(autouse=True)
def reset_runtime_state():
    """
    Keep tests isolated by resetting in-memory cache and rate-limit state.
    """
    from omniprice.core import cache as cache_module
    from omniprice.core import ratelimit as ratelimit_module

    cache_module._memory_cache.clear()
    cache_module._redis_client = None
    # Force tests to use in-memory fallback and avoid cross-test contamination from local Redis.
    cache_module._redis_init_attempted = True

    ratelimit_module._memory_buckets.clear()
    ratelimit_module._redis_client = None
    ratelimit_module._redis_init_attempted = True

    yield
