from __future__ import annotations

import asyncio
import json
import logging
import signal
import time
from typing import Any
from datetime import datetime

import httpx

from omniprice.core.config import settings
from omniprice.core.database import init_db
from omniprice.integrations.scraper.url_policy import extract_domain
from omniprice.models.scrape import ScrapeExecution
from omniprice.schemas.competitor import PriceHistoryCreate
from omniprice.services.competitor import CompetitorService
from omniprice.services.scraper import ScraperService

logger = logging.getLogger("omniprice.scrape_consumer")

_TRANSIENT_HTTP_STATUS = {408, 425, 429, 500, 502, 503, 504}


async def _process_payload(payload: dict[str, Any]) -> dict[str, Any]:
    url = str(payload.get("url", "")).strip()
    if not url:
        raise ValueError("Message payload missing 'url'")

    competitor = None
    competitor_id = payload.get("competitor_id")
    product_id = payload.get("product_id")

    if competitor_id:
        try:
            competitor = await CompetitorService.get_competitor(str(competitor_id))
            if not product_id:
                product_id = competitor.product_id
        except Exception as exc:
            logger.warning("Competitor lookup failed for %s: %s", competitor_id, exc)

    result = await ScraperService.fetch_price(url, allow_playwright_fallback=True)

    if competitor:
        await CompetitorService.update_price_snapshot(
            competitor,
            price=result.price,
            currency=result.currency,
            source=result.source,
            confidence=result.confidence,
        )

    if product_id:
        await CompetitorService.record_price_history(
            PriceHistoryCreate(
                product_id=str(product_id),
                competitor_id=str(competitor.id) if competitor else None,
                source_url=url,
                price=result.price,
                currency=result.currency,
                source=result.source,
                confidence=result.confidence,
            )
        )

    return {
        "url": url,
        "domain": extract_domain(url),
        "competitor_id": str(competitor.id) if competitor else None,
        "product_id": str(product_id) if product_id else None,
        "price": result.price,
        "currency": result.currency,
        "source": result.source,
        "confidence": result.confidence,
        "used_playwright": result.source.startswith("playwright->"),
    }


def _classify_failure(exc: Exception) -> tuple[str, str]:
    if isinstance(exc, ValueError):
        return ("permanent", "validation_error")
    if isinstance(exc, httpx.HTTPStatusError):
        code = exc.response.status_code
        if code in _TRANSIENT_HTTP_STATUS:
            return ("transient", f"http_{code}")
        return ("permanent", f"http_{code}")
    if isinstance(
        exc,
        (
            httpx.ConnectError,
            httpx.ConnectTimeout,
            httpx.ReadTimeout,
            httpx.WriteTimeout,
            httpx.PoolTimeout,
            httpx.RemoteProtocolError,
            httpx.NetworkError,
        ),
    ):
        return ("transient", exc.__class__.__name__.lower())
    error_name = exc.__class__.__name__.lower()
    if "timeout" in error_name:
        return ("transient", error_name)
    return ("transient", error_name)


async def _publish_json_message(
    channel,
    *,
    queue_name: str,
    payload: dict[str, Any],
    headers: dict[str, Any] | None = None,
) -> None:
    import aio_pika

    queue = await channel.declare_queue(queue_name, durable=True)
    message = aio_pika.Message(
        body=json.dumps(payload).encode("utf-8"),
        content_type="application/json",
        delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
        headers=headers or {},
    )
    await channel.default_exchange.publish(message, routing_key=queue.name)


async def _record_execution(**kwargs: Any) -> None:
    try:
        await ScrapeExecution(**kwargs).insert()
    except Exception:
        logger.exception("Failed to persist scrape execution event")


async def run_consumer() -> None:
    try:
        import aio_pika
    except ImportError as exc:
        raise RuntimeError("aio-pika is required for scrape worker") from exc

    await init_db()

    # Retry connection to RabbitMQ (essential for Cloud/Docker startup)
    connection = None
    for attempt in range(10):
        try:
            connection = await aio_pika.connect_robust(settings.RABBITMQ_URL)
            logger.info("Successfully connected to RabbitMQ")
            break
        except Exception as exc:
            logger.warning("RabbitMQ connection failed (attempt %s/10): %s", attempt + 1, exc)
            await asyncio.sleep(5)
    
    if not connection:
        raise RuntimeError("Failed to connect to RabbitMQ after 10 attempts")

    channel = await connection.channel()
    await channel.set_qos(prefetch_count=10)
    queue = await channel.declare_queue(settings.RABBITMQ_QUEUE_SCRAPE, durable=True)
    await channel.declare_queue(settings.RABBITMQ_QUEUE_SCRAPE_DLQ, durable=True)
    logger.info("Listening queue '%s' (DLQ: %s)", queue.name, settings.RABBITMQ_QUEUE_SCRAPE_DLQ)

    async def _on_message(message: aio_pika.IncomingMessage):
        started = time.perf_counter()
        headers = message.headers or {}
        retry_count = int(headers.get("x-retry-count", 0))
        try:
            payload = json.loads(message.body.decode("utf-8"))
        except Exception:
            logger.warning("Invalid message payload, dropping")
            await _record_execution(
                url="unknown",
                domain="unknown",
                status="invalid_payload",
                error_class="invalid_json",
                error_message="Invalid message payload",
                attempt=retry_count,
                latency_ms=int((time.perf_counter() - started) * 1000),
            )
            await message.reject(requeue=False)
            return

        try:
            result = await _process_payload(payload)
            await message.ack()
            await _record_execution(
                **result,
                status="success",
                attempt=retry_count,
                latency_ms=int((time.perf_counter() - started) * 1000),
            )
        except ValueError as exc:
            logger.warning("Dropping invalid job payload: %s", exc)
            dlq_payload = {
                "payload": payload,
                "failure": {
                    "error_class": "validation_error",
                    "error_message": str(exc),
                    "attempt": retry_count,
                    "failed_at": datetime.utcnow().isoformat() + "Z",
                },
            }
            await _publish_json_message(channel, queue_name=settings.RABBITMQ_QUEUE_SCRAPE_DLQ, payload=dlq_payload)
            await message.ack()
            await _record_execution(
                url=str(payload.get("url", "")),
                domain=extract_domain(str(payload.get("url", ""))) if payload.get("url") else "unknown",
                competitor_id=str(payload.get("competitor_id")) if payload.get("competitor_id") else None,
                product_id=str(payload.get("product_id")) if payload.get("product_id") else None,
                status="failed_permanent",
                error_class="validation_error",
                error_message=str(exc),
                attempt=retry_count,
                latency_ms=int((time.perf_counter() - started) * 1000),
            )
        except Exception as exc:
            failure_type, error_class = _classify_failure(exc)
            latency_ms = int((time.perf_counter() - started) * 1000)

            if failure_type == "transient" and retry_count < settings.SCRAPER_MAX_JOB_RETRIES:
                next_retry = retry_count + 1
                backoff_seconds = min(settings.SCRAPER_BACKOFF_BASE_SECONDS * (2**retry_count), 30)
                logger.warning(
                    "Transient scrape failure (%s). Retrying in %ss (attempt %s/%s)",
                    error_class,
                    backoff_seconds,
                    next_retry,
                    settings.SCRAPER_MAX_JOB_RETRIES,
                )
                await asyncio.sleep(backoff_seconds)
                retry_headers = dict(headers)
                retry_headers["x-retry-count"] = next_retry
                retry_headers["x-last-error"] = error_class
                await _publish_json_message(
                    channel,
                    queue_name=settings.RABBITMQ_QUEUE_SCRAPE,
                    payload=payload,
                    headers=retry_headers,
                )
                await message.ack()
                await _record_execution(
                    url=str(payload.get("url", "")),
                    domain=extract_domain(str(payload.get("url", ""))) if payload.get("url") else "unknown",
                    competitor_id=str(payload.get("competitor_id")) if payload.get("competitor_id") else None,
                    product_id=str(payload.get("product_id")) if payload.get("product_id") else None,
                    status="retry_scheduled",
                    error_class=error_class,
                    error_message=str(exc),
                    attempt=retry_count,
                    latency_ms=latency_ms,
                )
                return

            logger.exception("Worker failed to process message; sending to DLQ")
            dlq_payload = {
                "payload": payload,
                "failure": {
                    "error_class": error_class,
                    "error_message": str(exc),
                    "attempt": retry_count,
                    "failed_at": datetime.utcnow().isoformat() + "Z",
                },
            }
            await _publish_json_message(channel, queue_name=settings.RABBITMQ_QUEUE_SCRAPE_DLQ, payload=dlq_payload)
            await message.ack()
            await _record_execution(
                url=str(payload.get("url", "")),
                domain=extract_domain(str(payload.get("url", ""))) if payload.get("url") else "unknown",
                competitor_id=str(payload.get("competitor_id")) if payload.get("competitor_id") else None,
                product_id=str(payload.get("product_id")) if payload.get("product_id") else None,
                status="failed_transient" if failure_type == "transient" else "failed_permanent",
                error_class=error_class,
                error_message=str(exc),
                attempt=retry_count,
                latency_ms=latency_ms,
            )

    await queue.consume(_on_message, no_ack=False)

    stop_event = asyncio.Event()

    def _stop(*_: object):
        stop_event.set()

    loop = asyncio.get_running_loop()
    for sig in (signal.SIGTERM, signal.SIGINT):
        loop.add_signal_handler(sig, _stop)

    await stop_event.wait()
    await connection.close()


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    asyncio.run(run_consumer())


if __name__ == "__main__":
    main()
