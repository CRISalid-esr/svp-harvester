from abc import ABC, abstractmethod

from app.harvesters.abstract_references_converter import AbstractReferencesConverter
from app.settings.app_settings import AppSettings
from app.harvesters.abstract_harvester import AbstractHarvester


class AbstractHarvesterFactory(ABC):
    """
    Abstract factory for harvesters
    """

    @classmethod
    @abstractmethod
    def harvester(cls, settings: AppSettings) -> AbstractHarvester:  # pragma: no cover
        """Abstract factory main method ro return a concrete harvester instance"""

    @classmethod
    @abstractmethod
    def converter(cls) -> AbstractReferencesConverter:  # pragma: no cover
        """Abstract factory main method to return a concrete converter instance"""
