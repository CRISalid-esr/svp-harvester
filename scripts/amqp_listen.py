#!/usr/bin/env python
"""Basic publication code"""
import ast
import asyncio
import json

import aio_pika
from aio_pika import ExchangeType


async def main() -> None:
    """Main function"""
    connection = await aio_pika.connect_robust(
        "amqp://guest:guest@127.0.0.1/",
    )

    async with connection:
        routing_key = "event.references.reference.event"
        queue_name = "svp-scientific-repo"
        channel = await connection.channel()

        publication_exchange = await channel.declare_exchange(
            "publications", ExchangeType.TOPIC, durable=True
        )

        await channel.set_qos(prefetch_count=10)

        queue = await channel.declare_queue(queue_name, auto_delete=True)
        await queue.bind(publication_exchange, routing_key)

        async with queue.iterator() as queue_iter:
            async for message in queue_iter:
                async with message.process():
                    parsed_json = ast.literal_eval(message.body.decode("utf-8"))
                    # print pretty ascii separator with "message received" in the middle
                    print("".center(80, "*"))
                    print("".center(80, "="))
                    print("message received".center(80, "="))
                    print("".center(80, "="))
                    print(json.dumps(parsed_json, indent=4))
                    print("".center(80, "="))
                    print("".center(80, "*"))


if __name__ == "__main__":
    asyncio.run(main())
