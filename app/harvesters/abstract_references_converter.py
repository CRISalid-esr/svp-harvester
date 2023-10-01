from abc import ABC, abstractmethod

from app.db.models import Reference
from app.harvesters.abstract_harvester_raw_result import AbstractHarvesterRawResult


class AbstractReferencesConverter(ABC):
    """ "
    Abstract mother class for harvesters
    """

    @abstractmethod
    async def convert(self, raw_data: AbstractHarvesterRawResult) -> Reference:
        """
        Converts raw data from harvester source to a Normalised Reference object
        :param raw_data: Raw data from harvester source
        :return: Normalised Reference object
        """
