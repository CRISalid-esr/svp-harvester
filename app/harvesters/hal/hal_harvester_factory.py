from app.harvesters.abstract_harvester_factory import AbstractHarvesterFactory
from app.harvesters.abstract_references_converter import AbstractReferencesConverter
from app.harvesters.hal.hal_harvester import HalHarvester
from app.harvesters.hal.hal_references_converter import HalReferencesConverter


class HalHarvesterFactory(AbstractHarvesterFactory):
    """Idref harvester factory"""

    @classmethod
    def harvester(cls) -> HalHarvester:
        """Return IdrefHarvester instance"""
        return HalHarvester(converter=cls.converter())

    @classmethod
    def converter(cls) -> AbstractReferencesConverter:
        """Return HalReferencesConverter instance"""
        return HalReferencesConverter()
