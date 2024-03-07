from app.harvesters.abstract_harvester_factory import AbstractHarvesterFactory
from app.harvesters.scopus.scopus_harvester import ScopusHarvester
from app.harvesters.scopus.scopus_references_converter import ScopusReferencesConverter


class ScopusHarvesterFactory(AbstractHarvesterFactory):
    """Scopus harvester factory"""

    @classmethod
    def harvester(cls) -> ScopusHarvester:
        """
        Return ScopusHarvester instance
        """
        return ScopusHarvester(converter=cls.converter())

    @classmethod
    def converter(cls) -> ScopusReferencesConverter:
        """
        Return ScopusReferencesConverter instance
        """
        return ScopusReferencesConverter()
