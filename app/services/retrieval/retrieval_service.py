import asyncio
import importlib
from asyncio import Queue
from typing import Annotated, Optional

from fastapi import Depends
from starlette.background import BackgroundTasks

from app.config import get_app_settings
from app.db.conversions import EntityConverter
from app.db.daos.retrieval import RetrievalDAO
from app.db.daos.harvesting import HarvestingDAO
from app.db.models.retrieval import Retrieval
from app.db.models.harvesting import Harvesting
from app.db.models.entity import Entity
from app.db.session import async_session
from app.harvesters.abstract_harvester import AbstractHarvester
from app.harvesters.abstract_harvester_factory import AbstractHarvesterFactory
from app.services.entities.entity_resolution_service import EntityResolutionService
from app.settings.app_settings import AppSettings


class RetrievalService:
    """Main harvesters orchestration service"""

    def __init__(
        self,
        settings: Annotated[AppSettings, Depends(get_app_settings)],
        background_tasks: BackgroundTasks = None,
    ):
        """Init RetrievalService class"""
        self.settings = settings
        self.background_tasks = background_tasks
        self.harvesters: dict[str, AbstractHarvester] = {}
        self.retrieval: Optional[Retrieval] = None
        self.entity: Optional[Entity] = None

    async def register(self, entity: Entity) -> Retrieval:
        """Register a new retrieval with the associated entity"""
        self.entity = entity
        self._build_harvesters()
        async with async_session() as session:
            async with session.begin():
                db_entity: Entity = EntityConverter(entity).to_db_model()
                if existing_entity := await EntityResolutionService(session).resolve(
                    db_entity
                ):
                    db_entity = existing_entity
                else:
                    session.add(db_entity)
                self.retrieval = await RetrievalDAO(session).create_retrieval(db_entity)
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
            self.background_tasks.add_task(
                self._launch_harvesters, self.retrieval, result_queue
            )
        else:
            await self._launch_harvesters(self.retrieval, result_queue)

    def _build_harvesters(self):
        for harvester_config in self.settings.harvesters:
            factory_class = self._harvester_factory(
                harvester_config["module"], harvester_config["class"]
            )
            self.harvesters |= {
                f"{harvester_config['name']}": factory_class.harvester(self.settings)
            }

    @staticmethod
    def _harvester_factory(
        harvester_module: str, harvester_class: str
    ) -> AbstractHarvesterFactory:
        return getattr(importlib.import_module(harvester_module), harvester_class)

    async def _launch_harvesters(
        self, retrieval: Retrieval, result_queue: Queue = None
    ):
        pending_harvesters = []
        harvesting_tasks_index = {}
        for harvester_name, harvester in self.harvesters.items():
            if not harvester.is_relevant(self.entity):
                print(f"{harvester_name} will not run for {self.entity}")
                continue
            async with async_session() as session:
                async with session.begin():
                    harvesting = await HarvestingDAO(session).create_harvesting(
                        retrieval=retrieval,
                        harvester=harvester_name,
                        state=Harvesting.State.RUNNING,
                    )
            if result_queue is not None:
                harvester.set_result_queue(result_queue)
            harvester.set_entity_id(self.retrieval.entity_id)
            harvester.set_harvesting_id(harvesting.id)
            task = asyncio.create_task(
                harvester.run(),
                name=f"{harvester_name}_harvester_retrieval_{retrieval.id}",
            )
            pending_harvesters.append(task)
            harvesting_tasks_index[harvesting.id] = task

        while pending_harvesters:
            done_harvesters, pending_harvesters = await asyncio.wait(
                pending_harvesters, return_when=asyncio.FIRST_COMPLETED
            )
            print(f"done : {len(done_harvesters)} for {retrieval.id}")
            print(f"pending : {len(pending_harvesters)} for {retrieval.id}")
