"""Basic AMQP connectop,"""
import asyncio

import aio_pika


async def process_message(
    message: aio_pika.abc.AbstractIncomingMessage,
) -> None:
    """Process message"""
    async with message.process():
        print(message.body)
        await asyncio.sleep(1)


async def main() -> None:
    """Main function"""
    connection = await aio_pika.connect_robust(
        "amqp://guest:guest@127.0.0.1/",
    )

    queue_name = "spv-harvester-idref"

    # Creating channel
    channel = await connection.channel()

    # Maximum message count which will be processing at the same time.
    await channel.set_qos(prefetch_count=100)

    # Declaring queue
    queue = await channel.declare_queue(queue_name, auto_delete=True)

    await queue.consume(process_message)

    try:
        # Wait until terminate
        await asyncio.Future()
    finally:
        await connection.close()


if __name__ == "__main__":
    asyncio.run(main())
