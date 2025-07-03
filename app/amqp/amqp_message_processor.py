import asyncio
import json
import traceback
from datetime import datetime

from aio_pika import IncomingMessage
from aiormq import ChannelInvalidStateError, AMQPError
from asyncpg import PostgresConnectionError
from loguru import logger
from pydantic import ValidationError

from app.harvesters.exceptions.invalid_entity_error import InvalidEntityError
from app.models.people import Person
from app.services.retrieval.retrieval_service import RetrievalService
from app.settings.app_settings import AppSettings


class AMQPMessageProcessor:
    """
    Workers to process messages from AMQP interface
    """

    MAX_EXPECTED_RESULTS = 10000

    def __init__(
        self,
        task_queue: asyncio.Queue,
        result_queue: asyncio.Queue,
        settings: AppSettings,
    ):
        self.task_queue = task_queue
        self.result_queue = result_queue
        self.settings = settings

    async def wait_for_message(self, worker_id: int) -> None:
        """
        Messages awaiting method for async processing
        :param worker_id: queue worker identifier
        :return: None
        """
        message: IncomingMessage | None = None
        payload = None

        while True:
            requeue = False
            message = await self.task_queue.get()
            start_time = datetime.now()
            async with message.process(ignore_processed=True):
                payload = message.body
                try:
                    await self._process_message(payload)
                    await message.ack()
                    logger.debug(
                        f"Message {message.message_id}  processed by {worker_id} in "
                        f"{datetime.now() - start_time}"
                    )
                except ChannelInvalidStateError as channel_error:
                    await self._handle_channel_failure(channel_error, worker_id)
                    return
                except AMQPError as ack_error:
                    await self._handle_amqp_error(ack_error, worker_id)
                    requeue = True
                except KeyboardInterrupt as keyboard_interrupt:
                    await self._handle_application_stop(
                        keyboard_interrupt, message, worker_id
                    )
                except InvalidEntityError as invalid_entity_error:
                    await self._handle_invalid_entity(invalid_entity_error)
                    requeue = False  # except if we implement dead letter queue
                except (ConnectionError, PostgresConnectionError) as connection_error:
                    await self._handle_database_error(connection_error, worker_id)
                    requeue = True
                except Exception as exception:  # pylint: disable=broad-exception-caught
                    await self._handle_unexpected_error(exception, worker_id)
                    requeue = True
                finally:
                    await self._post_process_message(message, requeue, worker_id)
                    self.task_queue.task_done()
                    end_time = datetime.now()
                    logger.warning(
                        f"Performance : Message  processed by {worker_id} "
                        f"in {end_time - start_time} for payload {payload if payload else 'None'}"
                    )

    async def _post_process_message(self, message, requeue, worker_id):
        if message is not None and not message.processed:
            try:
                await message.nack(requeue=requeue)
            except ChannelInvalidStateError as channel_error:
                logger.error(
                    f"Error during message nack for {worker_id} : {channel_error}"
                )
            except AMQPError as nack_error:
                logger.error(
                    f"AMQP error during message nack for {worker_id} : {nack_error}"
                )

    async def _handle_unexpected_error(self, exception, worker_id):
        logger.error(
            f"Unexpected exception during {worker_id} message processing: {exception}"
        )
        logger.error(traceback.format_exc())

    async def _handle_database_error(self, connection_error, worker_id):
        logger.error(
            f"Connection refused during {worker_id} message processing : {connection_error}"
        )

    @staticmethod
    async def _handle_invalid_entity(invalid_entity_error):
        logger.error(f"Invalid entity submitted : {invalid_entity_error}")

    @staticmethod
    async def _handle_application_stop(keyboard_interrupt, message, worker_id):
        logger.warning(f"Amqp connect worker {worker_id} has been cancelled")
        if message is not None and not message.processed:
            await message.nack(requeue=True)
        raise keyboard_interrupt

    async def _handle_amqp_error(self, ack_error, worker_id):
        logger.error(f"AMQP error occurred during {worker_id} message ack: {ack_error}")

    async def _handle_channel_failure(self, channel_error, worker_id):
        logger.error(
            f"Channel invalid state error during {worker_id} "
            f"message ack: {channel_error}"
        )

    @staticmethod
    async def _get_message_payload(message, start_time, worker_id):
        payload: bytes | None = None
        async with message.process(ignore_processed=True):
            payload = message.body
            ack_time = datetime.now()
            logger.debug(
                f"Message {message.message_id}  acked by {worker_id} in {ack_time - start_time}"
            )
        return payload

    async def _process_message(self, payload: str):
        json_payload = json.loads(payload)
        reply_expected = json_payload.get("reply", False)

        if json_payload["type"] == "person":
            try:
                person = Person(**json_payload["fields"])
            except ValidationError as validation_error:
                await self.result_queue.put(
                    {
                        "type": "Retrieval",
                        "error": True,
                        "message": f"Entity validation error,"
                        f" retrieval aborted: {validation_error}",
                        "parameters": json_payload,
                    }
                )
                raise InvalidEntityError(
                    f"Entity validation error: {validation_error} in {json_payload}"
                ) from validation_error

            if person.has_no_bibliographic_identifiers():
                await self.result_queue.put(
                    {
                        "type": "Retrieval",
                        "error": True,
                        "message": "No identifiers provided, retrieval aborted",
                        "parameters": json_payload,
                    }
                )
                raise InvalidEntityError("No identifiers provided in {json_payload}")
            service = RetrievalService(
                identifiers_safe_mode=json_payload.get("identifiers_safe_mode", False),
                nullify=json_payload.get("nullify", False),
                harvesters=json_payload.get("harvesters", []),
                events=json_payload.get("events", []),
            )
            # Resister a new retrieval in DB
            retrieval = await service.register(entity=person)
            retrieval_id = retrieval.id
            del retrieval
            if reply_expected:
                await self.result_queue.put(
                    {
                        "type": "Retrieval",
                        "id": retrieval_id,
                        "message": "Retrieval started",
                    }
                )
            if reply_expected:
                await service.run(result_queue=self.result_queue)
            else:
                await service.run()
