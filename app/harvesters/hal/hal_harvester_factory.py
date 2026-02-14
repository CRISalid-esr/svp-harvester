from app.harvesters.abstract_harvester_factory import AbstractHarvesterFactory
from app.harvesters.abstract_references_converter import AbstractReferencesConverter
from app.harvesters.hal.hal_harvester import HalHarvester
from app.harvesters.hal.hal_references_converter import HalReferencesConverter


class HalHarvesterFactory(AbstractHarvesterFactory):
    """Idref harvester factory"""

    @classmethod
    def harvester(cls, name: str) -> HalHarvester:
        """Return HalHarvester instance"""
        return HalHarvester(converter=cls.converter(name))

    @classmethod
    def converter(cls, name: str) -> AbstractReferencesConverter:
        """Return HalReferencesConverter instance"""
        return HalReferencesConverter(name)
