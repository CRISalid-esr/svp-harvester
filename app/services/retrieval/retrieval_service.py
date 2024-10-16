import asyncio
import importlib
from asyncio import Queue
from typing import Annotated, Optional, List, Type

from fastapi import Depends, Body, HTTPException
from starlette.background import BackgroundTasks

from app.api.dependencies.event_types import event_types_or_default
from app.config import get_app_settings
from app.db.conversions import EntityConverter
from app.db.daos.retrieval_dao import RetrievalDAO
from app.db.daos.harvesting_dao import HarvestingDAO
from app.db.models.retrieval import Retrieval
from app.db.models.harvesting import Harvesting
from app.db.models.entity import Entity as DbEntity
from app.db.session import async_session
from app.harvesters.abstract_harvester import AbstractHarvester
from app.harvesters.abstract_harvester_factory import AbstractHarvesterFactory
from app.models.entities import Entity as PydanticEntity
from app.models.reference_events import ReferenceEvent
from app.services.entities.entity_resolution_service import EntityResolutionService


# pylint: disable=too-many-instance-attributes
class RetrievalService:
    """Main harvesters orchestration service"""

    # pylint: disable=too-many-arguments
    def __init__(
        self,
        background_tasks: BackgroundTasks = None,
        identifiers_safe_mode: Annotated[bool, Body()] = False,
        harvesters: Annotated[
            List[str], Body(examples=[["hal", "idref", "scanr", "openalex"]])
        ] = None,
        nullify: Annotated[List[str], Body(examples=[["id_hal_s"]])] = None,
        events: Annotated[
            List[ReferenceEvent.Type], Depends(event_types_or_default)
        ] = None,
        fetch_enhancements: Annotated[bool, Body()] = True,
    ):
        """Init RetrievalService class"""
        self.background_tasks = background_tasks
        self.harvesters_list: List[str] = harvesters
        self.harvesters: dict[str, AbstractHarvester] = {}
        self.retrieval: Optional[Retrieval] = None
        self.entity: Optional[Type[DbEntity]] = None
        self.identifiers_safe_mode = identifiers_safe_mode
        self.nullify = nullify
        self.events = events
        self.fetch_enhancements = fetch_enhancements

    async def register(
        self,
        entity: Type[PydanticEntity],
    ) -> Retrieval:
        """Register a new retrieval with the associated entity"""

        self._check_entity_declaration_and_nullification(entity)

        self._build_harvesters()
        # new entity is not saved to db yet
        new_entity: DbEntity = EntityConverter(entity).to_db_model()
        async with async_session() as session:
            async with session.begin():
                existing_entity = await EntityResolutionService(session).resolve(
                    new_entity,
                    nullify=self.nullify,
                    identifiers_safe_mode=self.identifiers_safe_mode,
                )
        self.entity = existing_entity or new_entity
        async with async_session() as session:
            async with session.begin():
                # this will add the new entity to the db if it does not exist
                self.retrieval = await RetrievalDAO(session).create_retrieval(
                    self.entity, event_types=self.events or []
                )
        return self.retrieval

    async def run(
        self, result_queue: Queue = None, in_background: bool = False
    ) -> None:
        """
        Run the retrieval process by launching the harvesters

        :param result_queue: The queue to push the results to
        :param in_background: If True, the harvesting will be launched in background
            (HTTP REST context only)
        :return: None
        """
        assert self.retrieval is not None, "Retrieval must be registered before running"
        if in_background:
            self.background_tasks.add_task(self._launch_harvesters, result_queue)
        else:
            await self._launch_harvesters(result_queue)

    def _build_harvesters(self):
        settings = get_app_settings()
        for harvester_config in settings.harvesters:
            if (
                self.harvesters_list is not None
                and harvester_config["name"] not in self.harvesters_list
            ):
                continue
            factory_class = self._harvester_factory(
                harvester_config["module"], harvester_config["class"]
            )
            self.harvesters |= {
                f"{harvester_config['name']}": factory_class.harvester()
            }

    @staticmethod
    def _harvester_factory(
        harvester_module: str, harvester_class: str
    ) -> AbstractHarvesterFactory:
        return getattr(importlib.import_module(harvester_module), harvester_class)

    async def _launch_harvesters(self, result_queue: Queue = None):
        pending_harvesters = []
        harvesting_tasks_index = {}
        for harvester_name, harvester in self.harvesters.items():
            if not harvester.is_relevant(self.entity):
                continue
            async with async_session() as session:
                async with session.begin():
                    harvesting = await HarvestingDAO(session).create_harvesting(
                        retrieval=self.retrieval,
                        harvester=harvester_name,
                        state=Harvesting.State.RUNNING,
                    )
            if result_queue is not None:
                harvester.set_result_queue(result_queue)
            harvester.set_entity_id(self.retrieval.entity_id)
            harvester.set_event_types(self.retrieval.event_types)
            harvester.set_fetch_enhancements(self.fetch_enhancements)
            harvester.set_harvesting_id(harvesting.id)
            task = asyncio.create_task(
                harvester.run(),
                name=f"{harvester_name}_harvester_retrieval_{self.retrieval.id}",
            )
            pending_harvesters.append(task)
            harvesting_tasks_index[harvesting.id] = task

        while pending_harvesters:
            _, pending_harvesters = await asyncio.wait(
                pending_harvesters, return_when=asyncio.FIRST_COMPLETED
            )

    def _check_entity_declaration_and_nullification(self, entity):
        if self.nullify:
            identifiers_set = set(identifier.type for identifier in entity.identifiers)
            nullify_set = set(self.nullify)
            intersection = identifiers_set.intersection(nullify_set)
            if intersection:
                conflicting_identifiers = ", ".join(intersection)
                raise HTTPException(
                    status_code=422,
                    detail=f"Unprocessable Entity: {conflicting_identifiers}"
                    f" cannot be declared and nullified at same time",
                )
