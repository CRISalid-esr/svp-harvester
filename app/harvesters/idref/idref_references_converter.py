from app.db.models.reference import Reference
from app.harvesters.abstract_harvester_raw_result import AbstractHarvesterRawResult
from app.harvesters.abstract_references_converter import AbstractReferencesConverter
from app.harvesters.idref.idref_basic_references_converter import (
    IdrefBasicReferencesConverter,
)
from app.harvesters.idref.idref_harvester import IdrefHarvester
from app.harvesters.idref.open_edition_references_converter import (
    OpenEditionReferencesConverter,
)
from app.harvesters.idref.persee_references_converter import PerseeReferencesConverter
from app.harvesters.idref.science_plus_references_converter import (
    SciencePlusReferencesConverter,
)
from app.harvesters.idref.sudoc_references_converter import SudocReferencesConverter
from app.harvesters.rdf_harvester_raw_result import (
    RdfHarvesterRawResult as RdfRawResult,
)
from app.harvesters.sparql_harvester_raw_result import (
    SparqlHarvesterRawResult as SparqlRawResult,
)


class IdrefReferencesConverter(AbstractReferencesConverter):
    """
    Converts raw data from IdRef to a normalised Reference object
    """

    def __init__(self):
        self.secondary_converter: AbstractReferencesConverter = None

    def build(self, raw_data: AbstractHarvesterRawResult) -> Reference:
        self._build_secondary_converter(raw_data)
        return super().build(raw_data=raw_data)

    async def convert(
        self, raw_data: RdfRawResult | SparqlRawResult, new_ref: Reference
    ) -> None:
        """
        Convert raw data from Idref and secondary sources to a normalised Reference object
        :param raw_data: raw data from Idref and secondary sources
        :param new_ref: Reference object
        :return: None
        """
        await self.secondary_converter.convert(raw_data=raw_data, new_ref=new_ref)

    def _build_secondary_converter(self, raw_data):
        if raw_data.formatter_name == IdrefHarvester.Formatters.SUDOC_RDF.value:
            self.secondary_converter = SudocReferencesConverter()
        if raw_data.formatter_name == IdrefHarvester.Formatters.SCIENCE_PLUS_RDF.value:
            self.secondary_converter = SciencePlusReferencesConverter()
        if raw_data.formatter_name == IdrefHarvester.Formatters.IDREF_SPARQL.value:
            self.secondary_converter = IdrefBasicReferencesConverter()
        if raw_data.formatter_name == IdrefHarvester.Formatters.OPEN_EDITION.value:
            self.secondary_converter = OpenEditionReferencesConverter()
        if raw_data.formatter_name == IdrefHarvester.Formatters.PERSEE_RDF.value:
            self.secondary_converter = PerseeReferencesConverter()
        assert self.secondary_converter, f"Unknown formatter {raw_data.formatter_name}"

    def _harvester(self) -> str:
        return "Idref"

    def hash(self, raw_data):
        return self.secondary_converter.hash(raw_data)

    def hash_keys(self):
        return self.secondary_converter.hash_keys()
