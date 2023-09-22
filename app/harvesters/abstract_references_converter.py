from abc import ABC, abstractmethod

from app.db.models import Reference


class AbstractReferencesConverter(ABC):
    """ "
    Abstract mother class for harvesters
    """

    @abstractmethod
    def convert(self, raw_data: dict) -> Reference:
        """
        Converts raw data from harvester source to a Normalised Reference object
        :param raw_data: Raw data from harvester source
        :return: Normalised Reference object
        """
