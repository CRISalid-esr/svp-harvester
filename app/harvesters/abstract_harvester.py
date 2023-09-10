from abc import ABC, abstractmethod
from asyncio import Event, Queue

from pydantic import BaseModel

from app.settings.app_settings import AppSettings


class AbstractHarvester(ABC):
    def __init__(self, settings: AppSettings):
        self.settings = settings

    @abstractmethod
    def relevant(self, entity: BaseModel) -> bool:
        pass

    @abstractmethod
    async def run(
        self, entity: BaseModel, harvesting_id: int, result_queue: Queue
    ) -> None:
        pass
