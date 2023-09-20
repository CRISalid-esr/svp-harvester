from abc import ABC, abstractmethod
from asyncio import Queue
from typing import Generator, Optional

from pydantic import BaseModel

from app.db.daos import EntityDAO, HarvestingDAO
from app.db.models import State, Harvesting, ReferenceEvent, Entity
from app.db.references.references_recorder import ReferencesRecorder
from app.db.session import async_session
from app.harvesters.abstract_references_converter import AbstractReferencesConverter
from app.harvesters.exceptions.external_api_error import ExternalApiError
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
    async def fetch_results(self) -> Generator[dict, None, None]:
        """
        Fetch the results from the external API
        :return: A generator of results
        """

    async def run(self) -> None:
        """
        Run the harvester asynchronously
        :return: None
        """
        await self._update_harvesting_state(State.RUNNING)
        await self._notify_harvesting_state()
        previous_references = await ReferencesRecorder().get_previous_references(
            self.entity_id
        )
        new_references = []
        try:
            async for result in self.fetch_results():
                reference = await self.converter.convert(result)
                reference_event: ReferenceEvent = await ReferencesRecorder().register(
                    harvesting=await self.get_harvesting(), new_ref=reference
                )
                await self._put_in_queue(
                    {
                        "type": "ReferenceEvent",
                        "id": reference_event.id,
                        "change": reference_event.type,
                    }
                )
                new_references.append(reference)
        except ExternalApiError as error:
            await self.handle_error(error)
        deleted_references = [
            ref for ref in previous_references if ref not in new_references
        ]
        for reference in deleted_references:
            reference_event = await ReferencesRecorder().register_deletion(
                harvesting=await self.get_harvesting(), old_ref=reference
            )
            await self._put_in_queue(
                {
                    "type": "ReferenceEvent",
                    "id": reference_event.id,
                    "change": ReferenceEvent.Type.DELETED.value,
                }
            )
        await self._update_harvesting_state(State.COMPLETED)
        await self._notify_harvesting_state()

    async def _notify_harvesting_state(self):
        await self._put_in_queue(
            {
                "type": "Harvesting",
                "id": self.harvesting_id,
                "state": (await self.get_harvesting()).state,
            }
        )

    async def _update_harvesting_state(self, state: State):
        async with async_session() as session:
            async with session.begin():
                await HarvestingDAO(session).update_harvesting_state(
                    self.harvesting_id, state
                )

    async def handle_error(self, error: ExternalApiError) -> None:
        """
        Persist and notify an error occurred during the harvesting
        :param error: The error message
        :return: None
        """
        await self._update_harvesting_state(State.FAILED)
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
