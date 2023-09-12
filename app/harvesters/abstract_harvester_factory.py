from abc import ABC, abstractmethod

from app.settings.app_settings import AppSettings
from app.harvesters.abstract_harvester import AbstractHarvester


class AbstractHarvesterFactory(ABC):
    @classmethod
    @abstractmethod
    def harvester(cls, settings: AppSettings) -> AbstractHarvester:  # pragma: no cover
        pass
