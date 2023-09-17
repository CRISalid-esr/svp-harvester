import asyncio

import aio_pika
from aio_pika import ExchangeType

from app.amqp.amqp_message_processor import AMQPMessageProcessor
from app.settings.app_settings import AppSettings

DEFAULT_RESULT_TIMEOUT = 600


class AMQPInterface:
    """Rabbitmq Connexion abstraction"""

    WAIT_BEFORE_SHUTDOWN = 30
    TASKS_BUFFERING_LIMIT = 5000
    TASKS_PARALLELISM_LIMIT = 1000
    INNER_TASKS_QUEUE_LENGTH = 10000
    EXCHANGE = "publications"
    KEYS = ["task.entity.references.retrieval"]

    def __init__(self, settings: AppSettings):
        """Init AMQP Connexion class"""
        self.settings = settings
        self.pika_queue: aio_pika.Queue | None = None
        self.pika_channel: aio_pika.Channel | None = None
        self.pika_exchange: aio_pika.Exchange | None = None
        self.pika_connexion: aio_pika.abc.AbstractRobustConnection | None = None
        self.inner_tasks_queue: asyncio.Queue | None = None
        self.message_processing_workers: list[asyncio.Task] | None = None

    async def listen(self):
        """Listen to AMQP queue"""
        await self._attach_message_processing_workers()
        await self._connect()
        await self._bind_queue()
        await self._listen_to_messages()

    async def stop_listening(self) -> None:
        """Stop listening to AMQP queue"""
        try:
            await asyncio.wait_for(
                self.inner_tasks_queue.join(), timeout=self.WAIT_BEFORE_SHUTDOWN
            )
        finally:
            for worker in self.message_processing_workers:
                worker.cancel()
            await self.pika_channel.close()
            await self.pika_connexion.close()

    async def _attach_message_processing_workers(self):
        self.message_processing_workers = []
        self.inner_tasks_queue = asyncio.Queue(maxsize=self.INNER_TASKS_QUEUE_LENGTH)
        for worker_id in range(self.TASKS_PARALLELISM_LIMIT):
            processor = await self._message_processor()
            self.message_processing_workers.append(
                asyncio.create_task(
                    processor.wait_for_message(worker_id),
                    name=f"amqp_message_processor_{worker_id}",
                )
            )

    async def _message_processor(self):
        return AMQPMessageProcessor(
            exchange=self.pika_exchange,
            tasks_queue=self.inner_tasks_queue,
            settings=self.settings,
        )

    async def _listen_to_messages(self):
        async with self.pika_queue.iterator() as queue_iter:
            async for message in queue_iter:
                # pylints warns about code that is pretty identical to official aiopika examples
                # https://aio-pika.readthedocs.io/en/latest/quick-start.html#simple-consumer
                async with message.process(ignore_processed=True):
                    async with message.process():
                        await self.inner_tasks_queue.put(message.body)

    async def _bind_queue(self) -> None:
        # Bind service message queue to publication exchange
        self.pika_exchange = await self.pika_channel.declare_exchange(
            self.EXCHANGE,
            ExchangeType.TOPIC,
        )
        await self.pika_channel.set_qos(prefetch_count=100)
        self.pika_queue = await self.pika_channel.declare_queue(
            self.settings.amqp_queue_name, durable=True
        )
        for key in self.KEYS:
            await self.pika_queue.bind(self.pika_exchange, routing_key=key)

    async def _connect(self) -> None:
        self.pika_connexion: aio_pika.Connection = await aio_pika.connect_robust(
            f"amqp://{self.settings.amqp_user}:"
            f"{self.settings.amqp_password}"
            f"@{self.settings.amqp_host}/",
        )
        self.pika_channel = await self.pika_connexion.channel()
