import asyncio
import json

import aio_pika
from aio_pika import ExchangeType

from app.db.models import Retrieval
from app.models.people import Person
from app.services.retrieval.retrieval_service import RetrievalService
from app.settings.app_settings import AppSettings

DEFAULT_RESULT_TIMEOUT = 600


class AMQPInterface:
    """Rabbitmq Connexion abstraction"""

    WAIT_BEFORE_SHUTDOWN = 30
    TASKS_BUFFERING_LIMIT = 5000
    TASKS_PARALLELISM_LIMIT = 1000
    MAX_EXPECTED_RESULTS = 10000
    EXCHANGE = "publications"
    KEYS = ["task.person.references.retrieval"]

    def __init__(self, settings: AppSettings):
        """Init AMQP Connexion class"""
        self.settings = settings
        self.queue: aio_pika.Queue | None = None
        self.channel: aio_pika.Channel | None = None
        self.connexion: aio_pika.abc.AbstractRobustConnection | None = None
        self.tasks_queue: asyncio.Queue | None = None
        self.workers: list[asyncio.Task] | None = None

    async def listen(self):
        """Listen to AMQP queue"""
        self.tasks_queue = asyncio.Queue(maxsize=self.MAX_EXPECTED_RESULTS)
        self.workers = [
            asyncio.create_task(
                self._message_processing_worker(worker_id),
                name=f"amqp_message_processor_{worker_id}",
            )
            for worker_id in range(self.TASKS_PARALLELISM_LIMIT)
        ]

        await self._connect()
        await self._bind_queue()
        async with self.queue.iterator() as queue_iter:
            async for message in queue_iter:
                # pylints warns about code that is pretty identical to official aiopika examples
                # https://aio-pika.readthedocs.io/en/latest/quick-start.html#simple-consumer
                async with message.process(ignore_processed=True):
                    async with message.process():
                        await self.tasks_queue.put(message.body)

    async def stop_listening(self) -> None:
        """Stop listening to AMQP queue"""
        try:
            await asyncio.wait_for(
                self.tasks_queue.join(), timeout=self.WAIT_BEFORE_SHUTDOWN
            )
        finally:
            for worker in self.workers:
                worker.cancel()
            await self.channel.close()
            await self.connexion.close()

    async def _message_processing_worker(self, worker_id: int) -> None:
        """Process message"""
        try:
            while True:
                payload: str = await self.tasks_queue.get()
                await self._process_message_payload(payload)
                self.tasks_queue.task_done()
        except KeyboardInterrupt:
            print(f"Amqp connect worker {worker_id} has been cancelled")

    async def _process_message_payload(
        self, payload: str, timeout=DEFAULT_RESULT_TIMEOUT
    ):
        json_payload = json.loads(payload)
        if json_payload["type"] == "person":
            # Create Pydantic object from fields
            person = Person(**json_payload["fields"])
            service = RetrievalService(self.settings)
            # Create a queue to get results back
            result_queue = asyncio.Queue(maxsize=self.MAX_EXPECTED_RESULTS)
            # Resister a new retrieval in DB
            retrieval = await service.register(entity=person)
            # Run the retrieval
            run = asyncio.create_task(
                service.run(result_queue=result_queue),
                name=f"amqp_retrieval_service_{retrieval.id}_launcher",
            )
            # Listen for results
            listen = asyncio.create_task(
                self._wait_for_result(
                    result_queue=result_queue, retrieval=retrieval, timeout=timeout
                ),
                name=f"amqp_retrieval_service_{retrieval.id}_listener",
            )
            # Wait for both tasks to finish
            await asyncio.gather(run, listen)

    async def _wait_for_result(
        self, result_queue: asyncio.Queue, retrieval: Retrieval, timeout: int
    ):
        try:
            while True:
                num = await asyncio.wait_for(result_queue.get(), timeout=timeout)
                print(f"Got result {num} for retrieval: {retrieval.id}")
        except asyncio.TimeoutError:
            print(f"Timeout while waiting for retrieval {retrieval.id} results ")
        except KeyboardInterrupt:
            print(f"Waiting for retrieval {retrieval.id} results interrupted by user")

    async def _bind_queue(self):
        # Bind service message queue to publication exchange
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

    async def _connect(self) -> None:
        self.connexion = await self._connexion()
        self.channel = await self.connexion.channel()

    async def _connexion(self) -> aio_pika.abc.AbstractRobustConnection:
        connexion: aio_pika.Connection = await aio_pika.connect_robust(
            f"amqp://{self.settings.amqp_user}:"
            f"{self.settings.amqp_password}"
            f"@{self.settings.amqp_host}/",
        )
        return connexion
