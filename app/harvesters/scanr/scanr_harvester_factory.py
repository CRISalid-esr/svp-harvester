from app.harvesters.abstract_harvester_factory import AbstractHarvesterFactory
from app.harvesters.abstract_references_converter import AbstractReferencesConverter
from app.harvesters.scanr.scanr_harvester import ScanrHarvester
from app.harvesters.scanr.scanr_references_converter import ScanrReferencesConverter
from app.settings.app_settings import AppSettings


class ScanrHarvesterFactory(AbstractHarvesterFactory):
    """Scanr harvester factory"""

    @classmethod
    def harvester(cls, settings: AppSettings) -> ScanrHarvester:
        """Return ScanrHarvester instance"""
        return ScanrHarvester(settings=settings, converter=cls.converter())

    @classmethod
    def converter(cls) -> AbstractReferencesConverter:
        """Return ScanrReferencesConverter instance"""
        return ScanrReferencesConverter()
