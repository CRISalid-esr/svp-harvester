import importlib
from typing import Annotated

from fastapi import Depends
from pydantic import BaseModel

from app.config import get_app_settings
from app.harvesters.abstract_harvester_factory import AbstractHarvesterFactory
from app.settings.app_settings import AppSettings


class RetrievalService:
    """Main harvesters orchestration service"""

    def __init__(
        self,
        settings: Annotated[AppSettings, Depends(get_app_settings)],
    ):
        """Init RetrievalService class"""
        self.settings = settings
        self.harvesters = {}
        self.entity = None

    async def retrieve_for(self, entity: BaseModel):
        self.entity = entity
        self._build_harvesters()
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
