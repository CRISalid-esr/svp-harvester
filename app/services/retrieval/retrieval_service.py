import asyncio
import importlib
from asyncio import Queue
from typing import Annotated

from fastapi import Depends
from pydantic import BaseModel
from starlette.background import BackgroundTasks

from app.config import get_app_settings
from app.db.conversions import EntityConverter
from app.db.daos import RetrievalDAO, HarvestingDAO
from app.db.models import Retrieval, State
from app.db.session import async_session
from app.harvesters.abstract_harvester import AbstractHarvester
from app.harvesters.abstract_harvester_factory import AbstractHarvesterFactory
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
        self.retrieval: Retrieval = None
        self.entity = None

    async def register(self, entity: BaseModel) -> Retrieval:
        """Register a new retrieval with the associated entity"""
        self.entity = entity
        self._build_harvesters()
        async with async_session() as session:
            async with session.begin():
                self.retrieval = await RetrievalDAO(session).create_retrieval(
                    # TODO first check if entity is already in database
                    EntityConverter(entity).to_db_model()
                )
        return self.retrieval

    async def run(
        self, result_queue: Queue = None, in_background: bool = False
    ) -> Retrieval:
        """Run the retrieval process by launching the harvesters"""
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
        async with async_session() as session:
            for harvester_name, harvester_class in self.harvesters.items():
                if not harvester_class.is_relevant(self.entity):
                    print(f"{harvester_name} while not run for {self.entity}")
                    continue
                harvesting = await HarvestingDAO(session).create_harvesting(
                    retrieval=retrieval,
                    harvester=harvester_name,
                    state=State.RUNNING,
                )
                if result_queue is not None:
                    await result_queue.put({"type": "Harvesting", "id": harvesting.id})
                pending_harvesters.append(
                    asyncio.create_task(
                        harvester_class.run(
                            entity=self.entity,
                            harvesting_id=harvesting.id,
                            result_queue=result_queue,
                        ),
                        name=f"{harvester_name}_harvester_retrieval_{retrieval.id}",
                    )
                )

        while pending_harvesters:
            done_harvesters, pending_harvesters = await asyncio.wait(
                pending_harvesters, return_when=asyncio.FIRST_COMPLETED
            )
            print(f"done : {len(done_harvesters)} for {retrieval.id}")
            print(f"pending : {len(pending_harvesters)} for {retrieval.id}")
