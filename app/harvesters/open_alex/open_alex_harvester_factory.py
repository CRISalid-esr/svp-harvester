from app.harvesters.abstract_harvester_factory import AbstractHarvesterFactory
from app.harvesters.open_alex.open_alex_harvester import OpenAlexHarvester
from app.harvesters.open_alex.open_alex_references_converter import (
    OpenAlexReferencesConverter,
)


class OpenAlexHarvesterFactory(AbstractHarvesterFactory):
    """OpenAlex harvester factory"""

    @classmethod
    def harvester(cls, name: str) -> OpenAlexHarvester:
        """
        Return OpenAlexHarvester instance
        """
        return OpenAlexHarvester(converter=cls.converter(name))

    @classmethod
    def converter(cls, name: str) -> OpenAlexReferencesConverter:
        """
        Return OpenAlexReferencesConverter instance
        """
        return OpenAlexReferencesConverter(name)
