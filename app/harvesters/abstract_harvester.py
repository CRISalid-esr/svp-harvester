from abc import ABC, abstractmethod
from asyncio import Queue
from typing import Optional, AsyncGenerator, Type, List
from loguru import logger

from app.api.dependencies.event_types import event_types_or_default
from app.db.daos.entity_dao import EntityDAO
from app.db.daos.harvesting_dao import HarvestingDAO
from app.db.daos.harvesting_error_dao import HarvestingErrorDAO
from app.db.models.entity import Entity as DbEntity
from app.db.models.harvesting import Harvesting
from app.db.models.reference_event import ReferenceEvent
from app.db.references.references_recorder import ReferencesRecorder
from app.db.session import async_session
from app.harvesters.abstract_harvester_raw_result import AbstractHarvesterRawResult
from app.harvesters.abstract_references_converter import AbstractReferencesConverter
from app.harvesters.exceptions.external_endpoint_failure import ExternalEndpointFailure
from app.harvesters.exceptions.unexpected_format_exception import (
    UnexpectedFormatException,
)
from app.models.references import Reference


class AbstractHarvester(ABC):
    """ "
    Abstract mother class for harvesters
    """

    supported_identifier_types: list[str] = []

    def __init__(self, converter: AbstractReferencesConverter):
        self.converter = converter
        self.result_queue: Optional[Queue] = None
        self.harvesting_id: Optional[int] = None
        self.harvesting: Optional[Harvesting] = None
        self.entity_id: Optional[int] = None
        self.entity: Optional[DbEntity] = None
        self.event_types: list[ReferenceEvent.Type] = []

    def set_result_queue(self, result_queue: Queue):
        """
        Set the result queue to allow the harvester to push the results back to the caller
        :param result_queue: The queue to push the results to
        :return: None
        """
        self.result_queue = result_queue

    def set_entity_id(self, entity_id: int):
        """
        Set the entity for which to harvest references
        :param entity_id: The entity for which to harvest references, person or organisation
        :return: None
        """
        self.entity_id = entity_id

    def set_harvesting_id(self, harvesting_id: int):
        """
        Set the id of the harvesting db entry representing the harvesting operation
        :param harvesting_id: The id of the harvesting
        :return: None
        """
        self.harvesting_id = harvesting_id

    def set_event_types(self, event_types: list[ReferenceEvent.Type]):
        """
        Set the event types for which to harvest references
        :param event_types: The event types for which to harvest references
        :return: None
        """
        self.event_types = event_types

    def is_relevant(self, entity: Type[DbEntity]) -> bool:  # pragma: no cover
        """
        Return True if the entity contains the required information for the harvester to do his job
        """
        return any(
            entity.get_identifier(identifier_type=identifier_type) is not None
            for identifier_type in self.supported_identifier_types
        )

    @abstractmethod
    async def fetch_results(
        self,
    ) -> AsyncGenerator[AbstractHarvesterRawResult, None]:
        """
        Fetch the results from the external API
        :return: A generator of results
        """

    async def run(self) -> None:
        """
        Run the harvester asynchronously
        :return: None
        """
        await self._update_harvesting_state(Harvesting.State.RUNNING)
        await self._notify_harvesting_state()
        references_recorder = ReferencesRecorder(
            harvesting=(await self.get_harvesting())
        )
        previous_references: list[Reference] = (
            await references_recorder.get_matching_references_before_harvesting(
                entity_id=self.entity_id
            )
            or []
        )
        existing_references: list[Reference] = []
        try:
            result: AbstractHarvesterRawResult
            async for result in self.fetch_results():
                if result is None or result == "end":
                    break
                new_ref = await self.converter.convert(result)
                assert (
                    new_ref.source_identifier is not None
                ), "Source identifier should be set on reference"
                # copy the harvester name from the harvesting to the reference
                new_ref.harvester = (await self.get_harvesting()).harvester
                old_ref = await references_recorder.exists(new_ref=new_ref)
                if old_ref is not None:
                    existing_references.append(old_ref)
                reference_event: Optional[
                    ReferenceEvent
                ] = await self._handle_converted_result(
                    new_ref=new_ref,
                    old_ref=old_ref,
                    references_recorder=references_recorder,
                )
                if reference_event is not None:
                    await self._put_in_queue(
                        {
                            "type": "ReferenceEvent",
                            "id": reference_event.id,
                            "change": reference_event.type,
                        }
                    )
            await self._register_deleted_references(
                existing_references=existing_references,
                previous_references=previous_references,
                references_recorder=references_recorder,
            )
            await self._update_harvesting_state(Harvesting.State.COMPLETED)
            await self._notify_harvesting_state()
        # main point to handle all errors related to external endpoints unavailability
        # harvester should let external ExternalEndpointFailure bubble up to this point
        # because the harvesting cant recover from them
        except ExternalEndpointFailure as error:
            await self.handle_error(error)
        # if an UnexpectedFormatException bubbles up to this point
        # it means that the harvester prefers to stop delivering results
        # but results may have been delivered before the exception
        # An harvester could decide to handle this exception on a lower level
        # and continue to deliver results
        except UnexpectedFormatException as error:
            await self.handle_error(error)
        # this is for debugging purpose only
        # as no other exception types are expected during normal execution
        # except Exception as error:
        #     raise error

    async def _handle_converted_result(
        self,
        new_ref: Reference,
        old_ref: Reference,
        references_recorder: ReferencesRecorder,
    ) -> Optional[ReferenceEvent]:
        reference_event: Optional[ReferenceEvent] = None
        if old_ref is not None:
            if (
                new_ref.hash != old_ref.hash
                and ReferenceEvent.Type.UPDATED.value
                in event_types_or_default(self.event_types)
            ):
                reference_event = await references_recorder.register_update(
                    new_ref=new_ref,
                    old_ref=old_ref,
                )
            if (
                new_ref.hash == old_ref.hash
                and ReferenceEvent.Type.UNCHANGED.value
                in event_types_or_default(self.event_types)
            ):
                reference_event = await references_recorder.register_unchanged(
                    old_ref=old_ref,
                )
        if (
            old_ref is None
            and ReferenceEvent.Type.CREATED.value
            in event_types_or_default(self.event_types)
        ):
            reference_event = await references_recorder.register_creation(
                new_ref=new_ref,
            )
        return reference_event

    async def _register_deleted_references(
        self,
        existing_references: List[Reference],
        previous_references: List[Reference],
        references_recorder: ReferencesRecorder,
    ):
        if ReferenceEvent.Type.DELETED.value not in self.event_types:
            return
        existing_references_identifiers = list(
            map(lambda ref: str(ref.source_identifier), existing_references)
        )
        deleted_references = [
            ref
            for ref in previous_references
            if str(ref.source_identifier) not in existing_references_identifiers
        ]
        for reference in deleted_references:
            reference_event = await references_recorder.register_deletion(
                old_ref=reference,
            )
            await self._put_in_queue(
                {
                    "type": "ReferenceEvent",
                    "id": reference_event.id,
                    "change": ReferenceEvent.Type.DELETED.value,
                }
            )

    async def _notify_harvesting_state(self):
        await self._put_in_queue(
            {
                "type": "Harvesting",
                "id": self.harvesting_id,
                "state": (await self.get_harvesting()).state,
            }
        )

    async def _update_harvesting_state(self, state: Harvesting.State):
        async with async_session() as session:
            async with session.begin():
                await HarvestingDAO(session).update_harvesting_state(
                    self.harvesting_id, state
                )

    async def _add_error_to_harvesting(self, error: Exception):
        async with async_session() as session:
            async with session.begin():
                await HarvestingErrorDAO(session).add_harvesting_error(
                    self.harvesting_id, error
                )

    async def handle_error(self, error: Exception) -> None:
        """
        Persist and notify an error occurred during the harvesting
        :param error: The error object
        :return: None
        """
        logger.error(error)
        await self._update_harvesting_state(Harvesting.State.FAILED)
        await self._add_error_to_harvesting(error)
        await self._put_in_queue(
            {
                "type": "Harvesting",
                "id": self.harvesting_id,
                "status": (await self.get_harvesting()).state,
                "message": str(error),
            }
        )

    async def _put_in_queue(self, message: dict) -> None:
        """
        Put a message in the result queue if it exists
        :param message: The message to put in the queue
        :return: None
        """
        if self.result_queue is None:
            return
        await self.result_queue.put(message)

    async def _get_entity(self) -> DbEntity:
        """
        Retrieve the entity for which to harvest references
        from the database if not already done
        :return: The entity for which to harvest references
        """
        if self.entity is None:
            async with async_session() as session:
                self.entity = await EntityDAO(session).get_entity_by_id(self.entity_id)
        return self.entity

    async def _get_entity_class_name(self) -> str:
        """
        Retrieve the entity class name for which to harvest references
        from the database if not already done
        :return: The entity class name for which to harvest references
        """
        entity = await self._get_entity()
        return entity.__class__.__name__

    async def get_harvesting(self) -> Harvesting:
        """
        Retrieve the harvesting db entry representing the harvesting operation
        from the database if not already done
        :return: The harvesting db entry representing the harvesting operation
        """
        if self.harvesting is None:
            async with async_session() as session:
                self.harvesting = await HarvestingDAO(session).get_harvesting_by_id(
                    self.harvesting_id
                )
        return self.harvesting
