from app.harvesters.abstract_harvester_factory import AbstractHarvesterFactory
from app.harvesters.open_alex.open_alex_harvester import OpenAlexHarvester
from app.harvesters.open_alex.open_alex_references_converter import (
    OpenAlexReferencesConverter,
)


class OpenAlexHarvesterFactory(AbstractHarvesterFactory):
    """OpenAlex harvester factory"""

    @classmethod
    def harvester(cls) -> OpenAlexHarvester:
        """
        Return OpenAlexHarvester instance
        """
        return OpenAlexHarvester(converter=cls.converter())

    @classmethod
    def converter(cls) -> OpenAlexReferencesConverter:
        """
        Return OpenAlexReferencesConverter instance
        """
        return OpenAlexReferencesConverter()
