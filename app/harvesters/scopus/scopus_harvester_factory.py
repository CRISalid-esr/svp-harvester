from app.harvesters.abstract_harvester_factory import AbstractHarvesterFactory
from app.harvesters.scopus.scopus_harvester import ScopusHarvester
from app.harvesters.scopus.scopus_references_converter import ScopusReferencesConverter


class ScopusHarvesterFactory(AbstractHarvesterFactory):
    """Scopus harvester factory"""

    @classmethod
    def harvester(cls, name: str) -> ScopusHarvester:
        """
        Return ScopusHarvester instance
        """
        return ScopusHarvester(converter=cls.converter(name))

    @classmethod
    def converter(cls, name: str) -> ScopusReferencesConverter:
        """
        Return ScopusReferencesConverter instance
        """
        return ScopusReferencesConverter(name)
