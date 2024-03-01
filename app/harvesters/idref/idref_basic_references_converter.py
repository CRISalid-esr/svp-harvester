from rdflib import FOAF

from app.db.models.abstract import Abstract
from app.db.models.reference import Reference
from app.db.models.reference_identifier import ReferenceIdentifier
from app.db.models.subtitle import Subtitle
from app.db.models.title import Title
from app.harvesters.abstract_references_converter import AbstractReferencesConverter
from app.harvesters.idref.idref_document_type_converter import (
    IdrefDocumentTypeConverter,
)
from app.harvesters.idref.idref_qualities_converter import IdrefQualitiesConverter
from app.harvesters.idref.rdf_resolver import RdfResolver
from app.harvesters.sparql_harvester_raw_result import (
    SparqlHarvesterRawResult as SparqlRawResult,
)
from app.services.concepts.concept_informations import ConceptInformations


class IdrefBasicReferencesConverter(AbstractReferencesConverter):
    """
    Converts raw data from IdRef to a normalised Reference object
    when data delivered by Idref Sparql endpoint are not enough to create
    a complete Reference object without the help of a secondary converter
    """

    def _harvester(self) -> str:
        return "Idref"

    @AbstractReferencesConverter.validate_reference
    async def convert(self, raw_data: SparqlRawResult, new_ref: Reference) -> None:
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

    def hash_keys(self):
        return ["uri", "role", "title", "type", "altLabel", "subject"]

    async def get_contributors(self, dict_payload):
        """
        Retrieves contributor information from the given dictionary payload.

        :params dict_payload: The dictionary payload containing author and role information.

        :return: A list of ContributionInformations objects.
        """
        contributor_informations = []
        for contributor in dict_payload.get("author", []):
            if contributor == "":
                continue
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
