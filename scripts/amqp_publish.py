#!/usr/bin/env python
"""Basic publication code"""
import asyncio
import json

import aio_pika
from aio_pika import ExchangeType, DeliveryMode


async def main() -> None:
    """Main function"""
    connection = await aio_pika.connect_robust(
        "amqp://guest:guest@127.0.0.1/",
    )

    async with connection:
        routing_key = "task.entity.references.retrieval"

        channel = await connection.channel()

        publication_exchange = await channel.declare_exchange(
            "publications",
            ExchangeType.TOPIC,
        )

        for _ in range(0, 1):
            payload = {
                "type": "person",
                "fields": {
                    "first_name": "Mary",
                    "last_name": "Researcher",
                    "identifiers": [{"type": "id_hal_i", "value": "744464"}],
                },
            }
            message = aio_pika.Message(
                json.dumps(payload).encode(),
                delivery_mode=DeliveryMode.PERSISTENT,
            )
            await publication_exchange.publish(
                message,
                routing_key=routing_key,
            )


if __name__ == "__main__":
    asyncio.run(main())
