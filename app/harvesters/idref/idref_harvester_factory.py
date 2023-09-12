from app.harvesters.abstract_harvester_factory import AbstractHarvesterFactory
from app.harvesters.idref.idref_harvester import IdrefHarvester
from app.settings.app_settings import AppSettings


class IdrefHarvesterFactory(AbstractHarvesterFactory):
    """Idref harvester factory"""

    @classmethod
    def harvester(cls, settings: AppSettings) -> IdrefHarvester:
        """Return IdrefHarvester instance"""
        return IdrefHarvester(settings)
