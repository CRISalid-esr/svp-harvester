import asyncio
from asyncio import sleep
from urllib.parse import quote

import aio_pika
from aio_pika import ExchangeType
from loguru import logger

from app.amqp.amqp_message_processor import AMQPMessageProcessor
from app.amqp.amqp_message_publisher import AMQPMessagePublisher
from app.settings.app_settings import AppSettings

DEFAULT_RESULT_TIMEOUT = 600


# pylint: disable=too-many-instance-attributes
class AMQPInterface:
    """Rabbitmq Connexion abstraction"""

    INNER_TASKS_QUEUE_LENGTH = 10000
    RESULT_QUEUE_LENGTH = 15

    def __init__(self, settings: AppSettings):
        """
        Init AMQP Connexion class

        :param settings: AppSettings
        :param state: fastapi app state

        """
        self.settings = settings
        self.pika_queue: aio_pika.Queue | None = None
        self.pika_channel: aio_pika.Channel | None = None
        self.pika_exchange: aio_pika.Exchange | None = None
        self.result_queue: asyncio.Queue | None = None
        self.publisher: AMQPMessagePublisher | None = None
        self.result_publisher_task: asyncio.Task | None = None
        self.pika_connexion: aio_pika.abc.AbstractRobustConnection | None = None
        self.task_queue: asyncio.Queue | None = None
        self.message_processing_workers: list[asyncio.Task] | None = None
        self.keys = [self.settings.amqp_retrieval_routing_key]

    async def connect(self):
        """Connect to AMQP queue"""
        await self._connect()
        await self._declare_exchange()
        await self._declare_publisher()
        await self._attach_message_processing_workers()
        await self._bind_queue()
        await sleep(0)

    async def stop_listening(self) -> None:
        """Stop listening to AMQP queue"""
        try:
            if self.task_queue is None:
                logger.warning("Inner tasks queue is not initialized, skipping join.")
            else:
                logger.info("Waiting for inner tasks queue to be empty before shutdown")
                await asyncio.wait_for(
                    self.task_queue.join(),
                    timeout=self.settings.amqp_wait_before_shutdown,
                )
            if self.result_publisher_task:
                self.result_publisher_task.cancel()
                try:
                    await self.result_publisher_task
                except asyncio.CancelledError:
                    logger.info("Result publisher task shut down cleanly")
        finally:
            for worker in self.message_processing_workers or []:
                worker.cancel()
            if self.pika_channel:
                logger.info("Closing AMQP channel")
                await self.pika_channel.close()
            if self.pika_connexion:
                logger.info("Closing AMQP connection")
                await self.pika_connexion.close()

    async def _attach_message_processing_workers(self):
        self.message_processing_workers = []
        self.task_queue = asyncio.Queue(maxsize=self.INNER_TASKS_QUEUE_LENGTH)
        for worker_id in range(self.settings.inner_task_parallelism_limit):
            processor = await self._message_processor()
            self.message_processing_workers.append(
                asyncio.create_task(
                    processor.wait_for_message(worker_id),
                    name=f"amqp_message_processor_{worker_id}",
                )
            )

    async def _message_processor(self):
        return AMQPMessageProcessor(
            task_queue=self.task_queue,
            result_queue=self.result_queue,
            settings=self.settings,
        )

    async def listen(self):
        """Listen to AMQP queue using prefetch-based flow control."""
        if not self.pika_queue:
            logger.error("Cannot listen: pika_queue is not initialized.")
            return

        logger.info("Starting AMQP listening loop (prefetch-controlled)")

        try:
            async with self.pika_queue.iterator() as queue_iter:
                async for message in queue_iter:
                    logger.debug(f"Received message: {message.body}")
                    await self.task_queue.put(message)
                    logger.debug(
                        f"Message queued. Inner queue size: {self.task_queue.qsize()}"
                    )
        except Exception as e:  # pylint: disable=broad-exception-caught
            logger.error(f"Exception during AMQP listening: {e}", exc_info=True)

    async def _declare_exchange(self) -> None:
        """
        Declare the publication exchange
        :return: None
        """
        self.pika_exchange = await self.pika_channel.declare_exchange(
            self.settings.amqp_exchange_name, ExchangeType.TOPIC, durable=True
        )

    async def _declare_publisher(self) -> None:
        """
        Declare the publisher
        :return: None
        """
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
                    f"Published result. Queue size: {self.result_queue.qsize()} - Result: {result}"
                )
                try:
                    await self.publisher.publish(result)
                except Exception as e:  # pylint: disable=broad-exception-caught
                    logger.exception(f"Failed to publish result: {e}")
                finally:
                    self.result_queue.task_done()
        except asyncio.CancelledError:
            logger.info("Result publisher task cancelled")

    async def _bind_queue(self) -> None:
        # Bind service message queue to publication exchange
        self.pika_queue = await self.pika_channel.declare_queue(
            self.settings.amqp_queue_name,
            durable=True,
            arguments={"x-consumer-timeout": self.settings.amqp_consumer_ack_timeout},
        )
        for key in self.keys:
            await self.pika_queue.bind(self.pika_exchange, routing_key=key)

    async def _connect(self) -> None:
        user = quote(self.settings.amqp_user)
        password = quote(self.settings.amqp_password)
        host = self.settings.amqp_host
        url = f"amqp://{user}:{password}@{host}/"
        self.pika_connexion: aio_pika.Connection = await aio_pika.connect_robust(url)
        self.pika_channel = await self.pika_connexion.channel(publisher_confirms=True)
        await self.pika_channel.set_qos(
            prefetch_count=self.settings.amqp_prefetch_count
        )
