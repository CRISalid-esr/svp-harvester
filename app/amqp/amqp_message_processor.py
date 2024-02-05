import asyncio
import json

import aio_pika
from loguru import logger
from pydantic import ValidationError

from app.amqp.amqp_message_publisher import AMQPMessagePublisher
from app.db.models.retrieval import Retrieval
from app.models.people import Person
from app.services.retrieval.retrieval_service import RetrievalService
from app.settings.app_settings import AppSettings

DEFAULT_RESULT_TIMEOUT = 600


class AMQPMessageProcessor:
    """
    Workers to process messages from AMQP interface
    """

    MAX_EXPECTED_RESULTS = 10000

    def __init__(
        self,
        exchange: aio_pika.Exchange,
        tasks_queue: asyncio.Queue,
        settings: AppSettings,
    ):
        self.exchange = exchange
        self.tasks_queue = tasks_queue
        self.settings = settings
        self._init_publisher()

    def _init_publisher(self) -> None:
        self.publisher = AMQPMessagePublisher(self.exchange)

    async def wait_for_message(self, worker_id: int) -> None:
        """
        Messages awaiting method for async processing
        :param worker_id: queue worker identifier
        :return: None
        """
        try:
            while True:
                payload: str = await self.tasks_queue.get()
                await self._process_message(payload)
                self.tasks_queue.task_done()
        except KeyboardInterrupt:
            logger.warning(f"Amqp connect worker {worker_id} has been cancelled")
        except Exception as exception:
            logger.error(
                f"Exception during {worker_id} message processing : {exception}"
            )
            raise exception

    async def _process_message(self, payload: str, timeout=DEFAULT_RESULT_TIMEOUT):
        json_payload = json.loads(payload)
        if json_payload["type"] == "person":
            try:
                person = Person(**json_payload["fields"])
            except ValidationError as validation_error:
                await self.publisher.publish(
                    {
                        "type": "Retrieval",
                        "error": True,
                        "message": f"Entity validation error,"
                        f" retrieval aborted: {validation_error}",
                        "parameters": json_payload,
                    }
                )
                return
            service = RetrievalService(
                history_safe_mode=json_payload.get("history_safe_mode"),
                identifiers_safe_mode=json_payload.get("identifiers_safe_mode"),
                nullify=json_payload.get("nullify"),
                harvesters=json_payload.get("harvesters"),
                events=json_payload.get("events"),
            )
            # Create a queue to get results back
            retrieval_results_queue = asyncio.Queue(maxsize=self.MAX_EXPECTED_RESULTS)
            # Resister a new retrieval in DB
            retrieval = await service.register(entity=person)
            await self.publisher.publish(
                {
                    "type": "Retrieval",
                    "id": retrieval.id,
                }
            )
            # Run the retrieval
            run = asyncio.create_task(
                service.run(result_queue=retrieval_results_queue),
                name=f"amqp_retrieval_service_{retrieval.id}_launcher",
            )
            # Listen for results
            listen = asyncio.create_task(
                self._wait_for_retrieval_result(
                    result_queue=retrieval_results_queue,
                    retrieval=retrieval,
                    timeout=timeout,
                ),
                name=f"amqp_retrieval_service_{retrieval.id}_listener",
            )
            # Wait for both tasks to finish
            await asyncio.gather(run, listen)

    async def _wait_for_retrieval_result(
        self, result_queue: asyncio.Queue, retrieval: Retrieval, timeout: int
    ):
        try:
            while True:
                result = await asyncio.wait_for(result_queue.get(), timeout=timeout)
                logger.debug(f"Got result {result} for retrieval: {retrieval.id}")
                await self.publisher.publish(result)
        except asyncio.TimeoutError:
            message = f"Retrieval {retrieval.id} results timeout"
            logger.warning(message)
            await self.publisher.publish(
                {
                    "type": "Retrieval",
                    "error": True,
                    "message": message,
                    "id": retrieval.id,
                }
            )
        except KeyboardInterrupt:
            message = f"Retrieval {retrieval.id} results processing has been cancelled"
            logger.warning(message)
            await self.publisher.publish(
                {
                    "type": "Retrieval",
                    "error": True,
                    "message": message,
                    "id": retrieval.id,
                }
            )
        except Exception as exception:
            message = f"Exception during retrieval {retrieval.id} results processing: {exception}"
            logger.error(message)
            await self.publisher.publish(
                {
                    "type": "Retrieval",
                    "error": True,
                    "message": message,
                    "id": retrieval.id,
                }
            )
            raise exception
