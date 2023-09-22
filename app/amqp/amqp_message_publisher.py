import aio_pika
from aio_pika import DeliveryMode

from app.amqp.amqp_harvesting_message_factory import AMQPHarvestingMessageFactory
from app.amqp.amqp_reference_event_message_factory import (
    AMQPReferenceEventMessageFactory,
)

DEFAULT_RESULT_TIMEOUT = 600


class AMQPMessagePublisher:
    """Rabbitmq Publisher abstraction"""

    def __init__(self, exchange: aio_pika.Exchange):
        """Init AMQP Publisher class"""
        self.exchange = exchange

    async def publish(self, content: dict) -> None:
        """Publish a message to the AMQP queue"""
        routing_key, payload = await self._build_message(content)
        if routing_key is None:
            return
        message = aio_pika.Message(
            str(payload).encode(),
            delivery_mode=DeliveryMode.PERSISTENT,
        )
        await self.exchange.publish(
            message=message,
            routing_key=routing_key,
        )
        print(str(payload))

    @staticmethod
    async def _build_message(content) -> tuple[str | None, str | None]:
        if content.get("type") == "Harvesting":
            return await AMQPHarvestingMessageFactory(content).build_message()
        if content.get("type") == "ReferenceEvent":
            return await AMQPReferenceEventMessageFactory(content).build_message()
        return None, None
