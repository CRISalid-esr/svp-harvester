import asyncio
import importlib
from typing import Annotated

from fastapi import Depends
from pydantic import BaseModel
from starlette.background import BackgroundTasks

from app.config import get_app_settings
from app.db.daos.retrieval_dao import RetrievalDAO
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
        self.entity = None

    async def retrieve_for(self, entity: BaseModel, asynchronous: bool = False):
        self.entity = entity
        self._build_harvesters()
        async with async_session() as session:
            async with session.begin():
                dao = RetrievalDAO(session)
                new_retrieval = await dao.create_retrieval()

        if asynchronous:
            self.background_tasks.add_task(self._launch_harvesters)
        else:
            await self._launch_harvesters()
        return True

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

    async def _launch_harvesters(self):
        pending_harvesters = [
            asyncio.create_task(harvester.run(self.entity))
            for harvester in self.harvesters.values()
        ]
        while pending_harvesters:
            done_harvesters, pending_harvesters = await asyncio.wait(
                pending_harvesters, return_when=asyncio.FIRST_COMPLETED
            )
            print(f"done : {len(done_harvesters)}")
            print(f"pending : {len(pending_harvesters)}")
