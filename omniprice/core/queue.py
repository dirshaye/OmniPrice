from __future__ import annotations

import json
from typing import Any

from omniprice.core.config import settings
from omniprice.core.exceptions import ServiceUnavailableException


async def publish_json_message(
    *,
    queue_name: str,
    payload: dict[str, Any],
) -> None:
    try:
        import aio_pika  # lazy import so local API still boots without queue deps installed
    except ImportError as exc:
        raise ServiceUnavailableException("Queue driver not installed (aio-pika)") from exc

    try:
        connection = await aio_pika.connect_robust(settings.RABBITMQ_URL)
    except Exception as exc:
        raise ServiceUnavailableException("RabbitMQ is unavailable") from exc

    try:
        channel = await connection.channel()
        await channel.set_qos(prefetch_count=10)
        queue = await channel.declare_queue(queue_name, durable=True)
        message = aio_pika.Message(
            body=json.dumps(payload).encode("utf-8"),
            content_type="application/json",
            delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
        )
        await channel.default_exchange.publish(message, routing_key=queue.name)
    finally:
        await connection.close()
