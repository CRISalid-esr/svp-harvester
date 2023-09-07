from app.harvesters.abstract_harvester import AbstractHarvester
from app.harvesters.abstract_harvester_factory import AbstractHarvesterFactory
from app.harvesters.scanr.scanr_harvester import ScanrHarvester
from app.settings.app_settings import AppSettings


class ScanrHarvesterFactory(AbstractHarvesterFactory):
    """Scanr harvester factory"""

    @classmethod
    def harvester(cls, settings: AppSettings) -> ScanrHarvester:
        """Return ScanrHarvester instance"""
        return ScanrHarvester(settings)
