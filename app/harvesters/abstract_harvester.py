from abc import ABC, abstractmethod
from asyncio import Queue

from pydantic import BaseModel

from app.settings.app_settings import AppSettings


class AbstractHarvester(ABC):
    """ "
    Abstract mother class for harvesters
    """

    def __init__(self, settings: AppSettings):
        self.settings = settings

    @abstractmethod
    def is_relevant(self, entity: BaseModel) -> bool:  # pragma: no cover
        """
        Return True if the entity contains the required information for the harvester to do his job
        """

    @abstractmethod
    async def run(
        self, entity: BaseModel, harvesting_id: int, result_queue: Queue
    ) -> None:  # pragma: no cover
        """Run the harvester asynchronously"""
