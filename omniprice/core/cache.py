from __future__ import annotations

import json
import time
from threading import Lock
from typing import Any, Optional

from omniprice.core.config import settings

_memory_cache: dict[str, tuple[float, str]] = {}
_memory_lock = Lock()
_redis_client: Any = None
_redis_init_attempted = False


async def _get_redis_client():
    global _redis_client, _redis_init_attempted
    if _redis_client is not None:
        return _redis_client
    if _redis_init_attempted:
        return None

    _redis_init_attempted = True
    try:
        import redis.asyncio as redis  # lazy import so app runs even without redis installed

        _redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)
        await _redis_client.ping()
        return _redis_client
    except Exception:
        _redis_client = None
        return None


def build_cache_key(*parts: str) -> str:
    return ":".join(p.strip() for p in parts if p is not None and str(p).strip())


async def cache_get_json(key: str) -> Optional[dict[str, Any]]:
    redis_client = await _get_redis_client()
    if redis_client:
        try:
            raw = await redis_client.get(key)
            if not raw:
                return None
            try:
                return json.loads(raw)
            except json.JSONDecodeError:
                return None
        except Exception:
            # Fail open to in-memory cache if redis is unavailable or loop-bound.
            pass

    with _memory_lock:
        record = _memory_cache.get(key)
        if not record:
            return None
        expires_at, raw = record
        if expires_at < time.time():
            _memory_cache.pop(key, None)
            return None
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            return None


async def cache_set_json(
    key: str,
    value: dict[str, Any],
    *,
    ttl_seconds: int | None = None,
) -> None:
    ttl = ttl_seconds if ttl_seconds is not None else settings.CACHE_DEFAULT_TTL_SECONDS
    raw = json.dumps(value)

    redis_client = await _get_redis_client()
    if redis_client:
        try:
            await redis_client.setex(key, max(ttl, 1), raw)
            return
        except Exception:
            # Fail open to in-memory cache if redis is unavailable or loop-bound.
            pass

    with _memory_lock:
        _memory_cache[key] = (time.time() + max(ttl, 1), raw)
