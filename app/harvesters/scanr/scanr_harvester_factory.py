from app.harvesters.abstract_harvester_factory import AbstractHarvesterFactory
from app.harvesters.scanr.scanr_harvester import ScanrHarvester
from app.harvesters.scanr.scanr_references_converter import ScanrReferencesConverter


class ScanrHarvesterFactory(AbstractHarvesterFactory):
    """Scanr harvester factory"""

    @classmethod
    def harvester(cls) -> ScanrHarvester:
        """Return ScanrHarvester instance"""
        return ScanrHarvester(converter=cls.converter())

    @classmethod
    def converter(cls) -> ScanrReferencesConverter:
        """Return ScanrReferencesConverter instance"""
        return ScanrReferencesConverter()
