"""
Script to emulate a sv harvester client that sends requests through the AMQP server
"""

import argparse
import asyncio
import csv
import json
import os

import aio_pika
from aio_pika import ExchangeType, DeliveryMode


def _parse_args():
    parser = argparse.ArgumentParser()
    # Required positional argument
    parser.add_argument(
        "--file",
        help="Researcher identifiers file",
        required=False,
        type=str,
        default=os.getenv("RESEARCH_IDS_FILE"),
    )
    return parser.parse_args()


async def _publish_requests(args):
    connection = await aio_pika.connect_robust(
        f"amqp://{os.getenv('AMQP_USER', 'guest')}:"
        f"{os.getenv('AMQP_PASSWORD', 'guest')}@"
        f"{os.getenv('AMQP_HOST', 'localhost')}:{os.getenv('AMQP_PORT', 5672)}"
    )
    async with connection:
        routing_key = "task.entity.references.retrieval"

        channel = await connection.channel()

        publication_exchange = await channel.declare_exchange(
            "publications",
            ExchangeType.TOPIC,
        )

        count = 0
        print(f"Reading file {args.file}")
        if not os.path.exists(args.file):
            print(f"File {args.file} does not exist")
            return
        with open(f"{args.file}", "r", encoding="UTF-8") as csv_file:
            reader = csv.DictReader(csv_file)
            for row in reader:
                count += 1
                print(f"row {count}")
                payload = {
                    "type": "person",
                    "identifiers_safe_mode": False,
                    "history_safe_mode": False,
                    "events": ["created", "updated", "deleted"],
                    "fields": {
                        "name": f"{row['last_name']}, {row['first_name']}",
                        "identifiers": [
                            {"type": key, "value": row[key]}
                            for key in row
                            if key in ["idref", "id_hal_i", "id_hal_s", "orcid"]
                            and row[key]
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
    args = _parse_args()
    asyncio.run(_publish_requests(args))
