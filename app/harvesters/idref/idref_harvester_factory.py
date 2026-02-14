from app.harvesters.abstract_harvester_factory import AbstractHarvesterFactory
from app.harvesters.idref.idref_harvester import IdrefHarvester
from app.harvesters.idref.idref_references_converter import IdrefReferencesConverter


class IdrefHarvesterFactory(AbstractHarvesterFactory):
    """Idref harvester factory"""

    @classmethod
    def harvester(cls, name: str) -> IdrefHarvester:
        """Return IdrefHarvester instance"""
        return IdrefHarvester(converter=cls.converter(name))

    @classmethod
    def converter(cls, name: str) -> IdrefReferencesConverter:
        """Return IdrefReferencesConverter instance"""
        return IdrefReferencesConverter(name)
