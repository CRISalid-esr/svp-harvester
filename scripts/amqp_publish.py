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
        routing_key = "task.person.references.retrieval"

        channel = await connection.channel()

        publication_exchange = await channel.declare_exchange(
            "publications",
            ExchangeType.TOPIC,
        )

        payload = {
            "type": "person",
            "fields": {
                "first_name": "John",
                "last_name": "Doe",
                "identifiers": [{"type": "orcid", "value": "0000-0002-1825-0097"}],
            },
        }
        for _ in range(0, 5):
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
