from rdflib import FOAF
from app.db.models.abstract import Abstract
from app.db.models.reference import Reference
from app.db.models.subtitle import Subtitle
from app.db.models.title import Title
from app.db.models.reference_identifier import ReferenceIdentifier
from app.harvesters.abstract_references_converter import AbstractReferencesConverter
from app.harvesters.idref.idref_document_type_converter import (
    IdrefDocumentTypeConverter,
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
from app.services.concepts.concept_informations import ConceptInformations


class IdrefReferencesConverter(AbstractReferencesConverter):
    """
    Converts raw data from IdRef to a normalised Reference object
    """

    async def convert(
        self, raw_data: RdfRawResult | SparqlRawResult
    ) -> Reference | None:
        """
        Convert raw data from IdRef to a normalised Reference object
        :param raw_data: raw data from IdRef
        :return: Reference object
        """
        if raw_data.formatter_name == IdrefHarvester.Formatters.SUDOC_RDF.value:
            return await SudocReferencesConverter().convert(raw_data)
        if raw_data.formatter_name == IdrefHarvester.Formatters.SCIENCE_PLUS_RDF.value:
            return await SciencePlusReferencesConverter().convert(raw_data)
        if raw_data.formatter_name == IdrefHarvester.Formatters.IDREF_SPARQL.value:
            return await self._convert_from_idref(raw_data)
        if raw_data.formatter_name == IdrefHarvester.Formatters.OPEN_EDITION.value:
            return await OpenEditionReferencesConverter().convert(raw_data)
        if raw_data.formatter_name == IdrefHarvester.Formatters.PERSEE_RDF.value:
            return await PerseeReferencesConverter().convert(raw_data)
        return None

    async def _convert_from_idref(self, raw_data: SparqlRawResult) -> Reference:
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
        new_ref.hash = self._hash(dict_payload)
        new_ref.source_identifier = uri
        return new_ref

    async def get_contributors(self, dict_payload):
        """
        Retrieves contributor information from the given dictionary payload.

        :params dict_payload: The dictionary payload containing author and role information.

        :return: A list of ContributionInformations objects.
        """
        contributor_informations = []
        for contributor in dict_payload["author"]:
            contributor = contributor.replace("/id", ".rdf")
            contributor = contributor.replace("http://", "https://")
            graph = await RdfResolver().fetch(contributor)
            contributor_name = ""
            for name in graph.objects(contributor, FOAF.name):
                contributor_name = name
            role = dict_payload["role"].split("/")[-1]
            contributor_informations.append(
                AbstractReferencesConverter.ContributionInformations(
                    role=IdrefQualitiesConverter.convert(role),
                    identifier=contributor,
                    name=contributor_name,
                    rank=None,
                )
            )

        return contributor_informations

    def _hash_keys(self):
        return ["uri", "role", "title", "type", "altLabel", "subject"]
