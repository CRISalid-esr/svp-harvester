#!/usr/bin/env python
"""Basic publication code"""
import asyncio
import json

import aio_pika
from aio_pika import ExchangeType, DeliveryMode

MIN_AUTHORS = 400
MAX_AUTHORS = 401


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

        # open identifiers_data.csv and read it line by line
        # for each line, create a payload and publish it
        count = 0
        with open("identifiers_data.csv", "r", encoding="UTF-8") as csv_file:
            next(csv_file)
            for line in csv_file:
                count += 1
                if count <= MIN_AUTHORS:
                    continue
                if count > MAX_AUTHORS:
                    break
                print(f"line {count}")

                line = line.split(",")
                # remove prefix 'https://www.idref.fr' from line 3 and remove trailing \n
                line[3] = line[3].replace("https://www.idref.fr/", "").strip("\n")
                payload = {
                    "type": "person",
                    "fields": {
                        "name": line[0],
                        "identifiers": [
                            {"type": "id_hal_s", "value": line[1]},
                            {"type": "id_hal_i", "value": line[2]},
                            {"type": "idref", "value": line[3]},
                        ],
                    },
                }
                message = aio_pika.Message(
                    body=json.dumps(payload).encode(),
                    delivery_mode=DeliveryMode.PERSISTENT,
                    content_type="application/json",
                )
                await publication_exchange.publish(
                    message,
                    routing_key=routing_key,
                )


if __name__ == "__main__":
    asyncio.run(main())
