"""Basic AMQP connectop,"""
import json

import aio_pika
from aio_pika import ExchangeType

from app.models.people import Person
from app.services.harvester.retrieval_service import RetrievalService
from app.settings.app_settings import AppSettings


class AMQPConnexion:
    """Rabbitmq Connexion abstraction"""

    EXCHANGE = "publications"
    KEYS = ["task.person.references.retrieval"]

    def __init__(self, settings: AppSettings):
        """Init AMQP Connexion class"""
        self.settings = settings
        self.queue: aio_pika.abc.AbstractQueue = None
        self.channel: aio_pika.abc.AbstractChannel = None

    async def listen(self):
        await self._bind_queue()
        async with self.queue.iterator() as queue_iter:
            async for message in queue_iter:
                async with message.process(ignore_processed=True):
                    await self._process_message(message)

    async def _process_message(
        self,
        message: aio_pika.abc.AbstractIncomingMessage,
    ) -> None:
        """Process message"""
        async with message.process():
            payload = json.loads(message.body)
            if payload["type"] == "person":
                person = Person(**payload["fields"])
                RetrievalService(person).retrieve()

    async def _bind_queue(self):
        exchange = await self.channel.declare_exchange(
            self.EXCHANGE,
            ExchangeType.TOPIC,
        )
        await self.channel.set_qos(prefetch_count=100)
        self.queue = await self.channel.declare_queue(
            self.settings.amqp_queue_name, durable=True
        )
        for key in self.KEYS:
            await self.queue.bind(exchange, routing_key=key)

    async def _connect(self) -> aio_pika.abc.AbstractChannel:
        connexion = await aio_pika.connect_robust(
            f"amqp://{self.settings.amqp_user}:"
            f"{self.settings.amqp_password}"
            f"@{self.settings.amqp_host}/",
        )
        self.channel = await connexion.channel()
