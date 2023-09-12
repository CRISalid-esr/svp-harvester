from abc import ABC, abstractmethod
from asyncio import Queue

from pydantic import BaseModel

from app.settings.app_settings import AppSettings


class AbstractHarvester(ABC):
    def __init__(self, settings: AppSettings):
        self.settings = settings

    @abstractmethod
    def is_relevant(self, entity: BaseModel) -> bool:  # pragma: no cover
        pass

    @abstractmethod
    async def run(
        self, entity: BaseModel, harvesting_id: int, result_queue: Queue
    ) -> None:  # pragma: no cover
        pass
