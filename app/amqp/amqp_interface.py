import asyncio
from asyncio import sleep
from urllib.parse import quote

import aio_pika
from aio_pika import ExchangeType
from loguru import logger

from app.amqp.amqp_message_processor import AMQPMessageProcessor
from app.amqp.amqp_message_publisher import AMQPMessagePublisher
from app.models.message_mode import MessageMode
from app.settings.app_settings import AppSettings

DEFAULT_RESULT_TIMEOUT = 600


# pylint: disable=too-many-instance-attributes
class AMQPInterface:
    """Rabbitmq Connexion abstraction"""

    INNER_TASKS_QUEUE_LENGTH = 10000

    # When this value is reached, workers will block on publishing
    RESULT_QUEUE_LENGTH = 10

    def __init__(self, settings: AppSettings):
        self.settings = settings
        self.interactive_queue: aio_pika.Queue | None = None
        self.batch_queue: aio_pika.Queue | None = None
        self.interactive_channel: aio_pika.Channel | None = None
        self.batch_channel: aio_pika.Channel | None = None
        self.pika_exchange: aio_pika.Exchange | None = None
        self.result_queue: asyncio.Queue | None = None
        self.publisher: AMQPMessagePublisher | None = None
        self.result_publisher_task: asyncio.Task | None = None
        self.pika_connexion: aio_pika.abc.AbstractRobustConnection | None = None
        self.interactive_task_queue: asyncio.Queue | None = None
        self.batch_task_queue: asyncio.Queue | None = None
        self.interactive_workers: list[asyncio.Task] | None = None
        self.batch_workers: list[asyncio.Task] | None = None

    async def connect(self):
        """Connect to AMQP queues"""
        await self._connect()
        await self._declare_exchange()
        await self._declare_publisher()
        await self._attach_message_processing_workers()
        await self._bind_queues()
        await sleep(0)

    async def stop_listening(self) -> None:
        """Stop listening to AMQP queues"""
        try:
            for task_queue, name in [
                (self.interactive_task_queue, "interactive"),
                (self.batch_task_queue, "batch"),
            ]:
                if task_queue is None:
                    logger.warning(
                        f"Inner {name} tasks queue is not initialized, skipping join."
                    )
                else:
                    logger.info(
                        f"Waiting for inner {name} tasks queue to be empty before shutdown"
                    )
                    await asyncio.wait_for(
                        task_queue.join(),
                        timeout=self.settings.amqp_wait_before_shutdown,
                    )
            if self.result_publisher_task:
                self.result_publisher_task.cancel()
                try:
                    await self.result_publisher_task
                except asyncio.CancelledError:
                    logger.info("Result publisher task shut down cleanly")
        finally:
            for worker in (self.interactive_workers or []) + (self.batch_workers or []):
                worker.cancel()
            if self.interactive_channel:
                logger.info("Closing interactive AMQP channel")
                await self.interactive_channel.close()
            if self.batch_channel:
                logger.info("Closing batch AMQP channel")
                await self.batch_channel.close()
            if self.pika_connexion:
                logger.info("Closing AMQP connection")
                await self.pika_connexion.close()

    async def _attach_message_processing_workers(self):
        self.interactive_task_queue = asyncio.Queue(maxsize=self.INNER_TASKS_QUEUE_LENGTH)
        self.batch_task_queue = asyncio.Queue(maxsize=self.INNER_TASKS_QUEUE_LENGTH)

        self.interactive_workers = []
        for worker_id in range(self.settings.inner_interactive_parallelism_limit):
            processor = await self._message_processor(self.interactive_task_queue)
            self.interactive_workers.append(
                asyncio.create_task(
                    processor.wait_for_message(worker_id),
                    name=f"amqp_message_processor_interactive_{worker_id}",
                )
            )

        self.batch_workers = []
        for worker_id in range(self.settings.inner_batch_parallelism_limit):
            processor = await self._message_processor(self.batch_task_queue)
            self.batch_workers.append(
                asyncio.create_task(
                    processor.wait_for_message(worker_id),
                    name=f"amqp_message_processor_batch_{worker_id}",
                )
            )

    async def _message_processor(self, task_queue: asyncio.Queue):
        return AMQPMessageProcessor(
            task_queue=task_queue,
            result_queue=self.result_queue,
            settings=self.settings,
        )

    async def listen(self):
        """Listen to both AMQP queues concurrently."""
        await asyncio.gather(
            self._listen_queue(self.interactive_queue, self.interactive_task_queue),
            self._listen_queue(self.batch_queue, self.batch_task_queue),
        )

    async def _listen_queue(
        self, pika_queue: aio_pika.Queue, task_queue: asyncio.Queue
    ) -> None:
        """Listen to a single AMQP queue using prefetch-based flow control."""
        if not pika_queue:
            logger.error("Cannot listen: pika_queue is not initialized.")
            return

        logger.info(
            f"Starting AMQP listening loop (prefetch-controlled) for {pika_queue.name}"
        )

        try:
            async with pika_queue.iterator() as queue_iter:
                async for message in queue_iter:
                    mode = MessageMode(message.routing_key.split(".")[-1])
                    logger.debug(f"Received message on {pika_queue.name}: {message.body}")
                    await task_queue.put((message, mode))
                    logger.debug(
                        f"Message queued. Inner queue size: {task_queue.qsize()}"
                    )
        except Exception as e:  # pylint: disable=broad-exception-caught
            logger.error(
                f"Exception during AMQP listening on {pika_queue.name}: {e}",
                exc_info=True,
            )

    async def _declare_exchange(self) -> None:
        self.pika_exchange = await self.interactive_channel.declare_exchange(
            self.settings.amqp_exchange_name, ExchangeType.TOPIC, durable=True
        )

    async def _declare_publisher(self) -> None:
        if self.publisher is None:
            self.publisher = AMQPMessagePublisher(self.pika_exchange)
        if self.result_queue is None:
            self.result_queue = asyncio.Queue(maxsize=self.RESULT_QUEUE_LENGTH)
            self.result_publisher_task = asyncio.create_task(
                self._publish_from_result_queue(), name="result_publisher"
            )

    async def _publish_from_result_queue(self):
        logger.info("Started result publisher loop")
        try:
            while True:
                result = await self.result_queue.get()
                logger.debug(
                    f"Publishing result. Queue size: {self.result_queue.qsize()} - Result: {result}"
                )
                try:
                    await self.publisher.publish(result)
                except Exception as e:  # pylint: disable=broad-exception-caught
                    logger.exception(f"Failed to publish result: {e}")
                finally:
                    self.result_queue.task_done()
        except asyncio.CancelledError:
            logger.info("Result publisher task cancelled")

    async def _bind_queues(self) -> None:
        self.interactive_queue = await self.interactive_channel.declare_queue(
            self.settings.amqp_interactive_queue_name,
            durable=True,
            arguments={
                "x-consumer-timeout": self.settings.amqp_consumer_ack_timeout,
                "x-dead-letter-exchange": "dlx.publications",
                "x-dead-letter-routing-key": self.settings.amqp_interactive_queue_name,
            },
        )
        await self.interactive_queue.bind(
            self.pika_exchange,
            routing_key=self.settings.amqp_interactive_routing_key,
        )

        self.batch_queue = await self.batch_channel.declare_queue(
            self.settings.amqp_batch_queue_name,
            durable=True,
            arguments={
                "x-consumer-timeout": self.settings.amqp_consumer_ack_timeout,
                "x-dead-letter-exchange": "dlx.publications",
                "x-dead-letter-routing-key": self.settings.amqp_batch_queue_name,
            },
        )
        await self.batch_queue.bind(
            self.pika_exchange,
            routing_key=self.settings.amqp_batch_routing_key,
        )

    async def _connect(self) -> None:
        user = quote(self.settings.amqp_user)
        password = quote(self.settings.amqp_password)
        host = self.settings.amqp_host
        url = f"amqp://{user}:{password}@{host}/"
        self.pika_connexion: aio_pika.Connection = await aio_pika.connect_robust(url)
        self.interactive_channel = await self.pika_connexion.channel(
            publisher_confirms=True
        )
        await self.interactive_channel.set_qos(
            prefetch_count=self.settings.amqp_interactive_prefetch_count
        )
        self.batch_channel = await self.pika_connexion.channel(publisher_confirms=True)
        await self.batch_channel.set_qos(
            prefetch_count=self.settings.amqp_batch_prefetch_count
        )
