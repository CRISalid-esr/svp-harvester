import aio_pika
from aio_pika import DeliveryMode

from app.api.amqp.amqp_harvesting_message_factory import AMQPHarvestingMessageFactory

DEFAULT_RESULT_TIMEOUT = 600


class AMQPPublisher:
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
            message,
            routing_key=routing_key,
        )
        print(str(payload))

    @staticmethod
    async def _build_message(content) -> tuple[str, str]:
        if content.get("type") == "Harvesting":
            return await AMQPHarvestingMessageFactory(content).build_message()
        return None, None
