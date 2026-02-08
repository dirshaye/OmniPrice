from __future__ import annotations

import time
from collections import defaultdict
from threading import Lock
from typing import Any

from fastapi import HTTPException, Request, status

from omniprice.core.config import settings
from omniprice.core.security import decode_token

_redis_client: Any = None
_redis_init_attempted = False
_memory_buckets: dict[str, list[float]] = defaultdict(list)
_memory_lock = Lock()


async def _get_redis_client():
    global _redis_client, _redis_init_attempted
    if _redis_client is not None:
        return _redis_client
    if _redis_init_attempted:
        return None
    _redis_init_attempted = True
    try:
        import redis.asyncio as redis  # lazy import

        _redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)
        await _redis_client.ping()
        return _redis_client
    except Exception:
        _redis_client = None
        return None


def _extract_subject(request: Request) -> str:
    auth_header = request.headers.get("authorization", "")
    if auth_header.lower().startswith("bearer "):
        token = auth_header.split(" ", 1)[1].strip()
        try:
            payload = decode_token(token)
            subject = payload.get("sub")
            if isinstance(subject, str) and subject:
                return f"user:{subject}"
        except Exception:
            pass
    client_host = request.client.host if request.client else "unknown"
    return f"ip:{client_host}"


def rate_limit_dependency(
    *,
    namespace: str,
    max_requests: int,
    window_seconds: int,
):
    async def _enforce(request: Request):
        subject = _extract_subject(request)
        now = time.time()
        bucket_key = f"ratelimit:{namespace}:{subject}:{int(now // window_seconds)}"

        redis_client = await _get_redis_client()
        if redis_client:
            try:
                count = await redis_client.incr(bucket_key)
                if count == 1:
                    await redis_client.expire(bucket_key, window_seconds)
                if count > max_requests:
                    raise HTTPException(
                        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                        detail=f"Rate limit exceeded for {namespace}. Try again later.",
                    )
                return
            except Exception:
                # Fail open to in-memory limiter if redis is unavailable or loop-bound.
                pass

        with _memory_lock:
            window_start = now - window_seconds
            bucket = [t for t in _memory_buckets[bucket_key] if t >= window_start]
            bucket.append(now)
            _memory_buckets[bucket_key] = bucket
            if len(bucket) > max_requests:
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail=f"Rate limit exceeded for {namespace}. Try again later.",
                )

    return _enforce
