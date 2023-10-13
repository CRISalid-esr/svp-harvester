from abc import ABC, abstractmethod
from asyncio import Queue
from typing import Optional, AsyncGenerator

from pydantic import BaseModel

from app.db.daos.entity_dao import EntityDAO
from app.db.daos.harvesting_dao import HarvestingDAO
from app.db.models.entity import Entity
from app.db.models.reference_event import ReferenceEvent
from app.db.models.harvesting import Harvesting
from app.db.references.references_recorder import ReferencesRecorder
from app.db.session import async_session
from app.harvesters.abstract_harvester_raw_result import AbstractHarvesterRawResult
from app.harvesters.abstract_references_converter import AbstractReferencesConverter
from app.harvesters.exceptions.external_endpoint_failure import ExternalEndpointFailure
from app.harvesters.exceptions.unexpected_format_exception import (
    UnexpectedFormatException,
)
from app.settings.app_settings import AppSettings


class AbstractHarvester(ABC):
    """ "
    Abstract mother class for harvesters
    """

    def __init__(self, settings: AppSettings, converter: AbstractReferencesConverter):
        self.settings = settings
        self.converter = converter
        self.result_queue: Optional[Queue] = None
        self.harvesting_id: Optional[int] = None
        self.harvesting: Optional[Harvesting] = None
        self.entity_id: Optional[int] = None
        self.entity: Optional[Entity] = None

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

    @abstractmethod
    def is_relevant(self, entity: BaseModel) -> bool:  # pragma: no cover
        """
        Return True if the entity contains the required information for the harvester to do his job
        """

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
        previous_references = await ReferencesRecorder().get_previous_references(
            self.entity_id, (await self.get_harvesting()).harvester
        )
        new_references = []
        try:
            result: AbstractHarvesterRawResult
            async for result in self.fetch_results():
                if result is None or result == "end":
                    break
                reference = await self.converter.convert(result)
                if reference is None:
                    # TODO log something
                    continue
                assert (
                    reference.source_identifier is not None
                ), "Source identifier should be set on reference"
                # copy the harvester name from the harvesting to the reference
                reference.harvester = (await self.get_harvesting()).harvester
                reference_event: ReferenceEvent = await ReferencesRecorder().register(
                    harvesting_id=(await self.get_harvesting()).id, new_ref=reference
                )
                await self._put_in_queue(
                    {
                        "type": "ReferenceEvent",
                        "id": reference_event.id,
                        "change": reference_event.type,
                    }
                )
                new_references.append(reference)
            new_references_source_identifiers = [
                str(ref.source_identifier) for ref in new_references
            ]
            deleted_references = [
                ref
                for ref in previous_references
                if str(ref.source_identifier) not in new_references_source_identifiers
            ]
            for reference in deleted_references:
                reference_event = await ReferencesRecorder().register_deletion(
                    harvesting_id=(await self.get_harvesting()).id, old_ref=reference
                )
                await self._put_in_queue(
                    {
                        "type": "ReferenceEvent",
                        "id": reference_event.id,
                        "change": ReferenceEvent.Type.DELETED.value,
                    }
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
        # in which case it will not bubble up to this point
        except UnexpectedFormatException as error:
            await self.handle_error(error)

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

    async def handle_error(self, error: Exception) -> None:
        """
        Persist and notify an error occurred during the harvesting
        :param error: The error object
        :return: None
        """
        # TODO add informations about the error to the harvesting
        await self._update_harvesting_state(Harvesting.State.FAILED)
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

    async def _get_entity(self) -> Entity:
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
