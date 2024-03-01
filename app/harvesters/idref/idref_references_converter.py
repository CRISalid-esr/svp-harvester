from rdflib import FOAF
from app.db.models.abstract import Abstract
from app.db.models.reference import Reference
from app.harvesters.abstract_harvester_raw_result import AbstractHarvesterRawResult
from app.harvesters.abstract_references_converter import AbstractReferencesConverter
from app.harvesters.idref.idref_basic_references_converter import (
    IdrefBasicReferencesConverter,
)
from app.harvesters.idref.idref_harvester import IdrefHarvester
from app.harvesters.idref.idref_qualities_converter import IdrefQualitiesConverter
from app.harvesters.idref.open_edition_references_converter import (
    OpenEditionReferencesConverter,
)
from app.harvesters.idref.persee_references_converter import PerseeReferencesConverter
from app.harvesters.idref.rdf_resolver import RdfResolver
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


    @AbstractReferencesConverter.validate_reference
    async def _convert_from_idref(self, raw_data: SparqlRawResult) -> Reference | None:
        new_ref = Reference()
        dict_payload: dict = raw_data.payload
        uri = raw_data.source_identifier

        for title in dict_payload["title"]:
            new_ref.titles.append(Title(value=title, language="fr"))
        for subtitle in dict_payload["altLabel"]:
            new_ref.subtitles.append(Subtitle(value=subtitle, language="fr"))
        for abstract in dict_payload["note"]:
            new_ref.abstracts.append(Abstract(value=abstract, language="fr"))
        concept_informations = [
            ConceptInformations(
                uri=subject.get("uri"), label=subject.get("label"), language="fr"
            )
            for subject in dict_payload["subject"].values()
        ]
        new_ref.subjects.extend(
            await self._get_or_create_concepts_by_uri(concept_informations)
        )

        for document_type in dict_payload["type"]:
            uri_type, label = IdrefDocumentTypeConverter().convert(document_type)
            new_ref.document_type.append(
                await self._get_or_create_document_type_by_uri(uri_type, label)
            )

        async for contribution in self._contributions(
            contribution_informations=await self.get_contributors(dict_payload),
            source="idref",
        ):
            new_ref.contributions.append(contribution)

        new_ref.identifiers.append(ReferenceIdentifier(value=uri, type="uri"))

    def _harvester(self) -> str:
        return "Idref"

    def hash(self, raw_data):
        return self.secondary_converter.hash(raw_data)

    def hash_keys(self):
        return self.secondary_converter.hash_keys()
