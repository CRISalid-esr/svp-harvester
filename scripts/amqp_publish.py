#!/usr/bin/env python
"""Basic publication code"""
import asyncio

import aio_pika


async def main() -> None:
    """Main function"""
    connection = await aio_pika.connect_robust(
        "amqp://guest:guest@127.0.0.1/",
    )

    async with connection:
        routing_key = "task.person.references.fetch"

        channel = await connection.channel()

        await channel.default_exchange.publish(
            aio_pika.Message(body=f"Hello {routing_key}".encode()),
            routing_key=routing_key,
        )


if __name__ == "__main__":
    asyncio.run(main())
