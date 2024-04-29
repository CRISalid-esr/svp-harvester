import urllib
import rdflib

from rdflib import RDF, Literal, DCTERMS, Namespace
from semver import Version

from app.config import get_app_settings
from app.db.models.reference_identifier import ReferenceIdentifier
from app.db.models.reference import Reference

from app.db.models.title import Title
from app.harvesters.exceptions.unexpected_format_exception import (
    UnexpectedFormatException,
)
from app.harvesters.idref.abes_rdf_references_converter import (
    AbesRDFReferencesConverter,
)
from app.harvesters.idref.rdf_resolver import RdfResolver
from app.harvesters.idref.science_plus_document_type_converter import (
    SciencePlusDocumentTypeConverter,
)
from app.harvesters.idref.science_plus_roles_converter import (
    SciencePlusRolesConverter,
)
from app.harvesters.rdf_harvester_raw_result import RdfHarvesterRawResult
from app.services.hash.hash_key import HashKey
from app.services.issue.issue_data_class import IssueInformations
from app.services.journal.journal_data_class import JournalInformations


class SciencePlusReferencesConverter(AbesRDFReferencesConverter):
    """
    Converts raw data from SciencePlus to a normalised Reference object
    """

    HUB_NAMESPACE = Namespace("http://hub.abes.fr/namespace/")
    BIBO_NAMESPACE = Namespace("http://purl.org/ontology/bibo/")
    SCIENCE_PLUS_QUERY_SUFFIX = "https://scienceplus.abes.fr/sparql"

    def __init__(self):
        super().__init__()
        self._source = "science_plus"
        self.pub_graph = None
        self.uri = None

    def _harvester(self) -> str:
        return "Idref"

    @AbesRDFReferencesConverter.validate_reference
    async def convert(
        self, raw_data: RdfHarvesterRawResult, new_ref: Reference
    ) -> None:
        self.pub_graph = raw_data.payload
        self.uri = raw_data.source_identifier
        await super().convert(raw_data=raw_data, new_ref=new_ref)
        if not new_ref.titles:
            raise UnexpectedFormatException(
                f"Science Plus reference without title: {new_ref.source_identifier}"
            )
        if raw_data.doi:
            new_ref.identifiers.append(self._add_doi_identifier(raw_data.doi))

    async def _get_bibliographic_resource(self, pub_graph, uri):
        for document in pub_graph.objects(
            rdflib.term.URIRef(uri), self.HUB_NAMESPACE.isPartOfThisJournal
        ):
            document_uri = document
            document = await self._query_ressource(document)
            yield document, document_uri
            break

    async def _get_journal(self, biblio_graph, uri):
        titles = []
        for title in biblio_graph.objects(rdflib.term.URIRef(uri), DCTERMS.title):
            titles.append(title.value)
        publisher_name = None
        for publisher in biblio_graph.objects(
            rdflib.term.URIRef(uri), self.HUB_NAMESPACE.publisher
        ):
            publisher_name = publisher.value
        return await self._get_or_create_journal(
            JournalInformations(
                source="science_plus",
                source_identifier=uri,
                titles=titles,
                publisher=publisher_name,
            )
        )

    async def _get_issue(self, biblio_graph, uri, journal):
        # Fetch the issue data
        issue = None
        for issue in self.pub_graph.objects(
            rdflib.term.URIRef(self.uri), DCTERMS.isPartOf
        ):
            issue_uri = issue
            issue = await self._query_ressource(issue)

        number_value = None
        for number in issue.objects(
            rdflib.term.URIRef(issue_uri), self.BIBO_NAMESPACE.issue
        ):
            number_value = number.value

        issued_value = None
        for issued in issue.objects(rdflib.term.URIRef(issue_uri), DCTERMS.issued):
            issued_value = str(issued.value)

        rights_value = None
        for rights in issue.objects(rdflib.term.URIRef(issue_uri), DCTERMS.rights):
            rights_value = rights.value

        titles = []
        for title in issue.objects(rdflib.term.URIRef(issue_uri), DCTERMS.title):
            titles.append(title.value)

        return await self._get_or_create_issue(
            IssueInformations(
                source="science_plus",
                source_identifier=issue_uri,
                journal=journal,
                number=number_value,
                volume=self._get_volume_issue(issue_uri),
                date=issued_value,
                rights=rights_value,
                titles=titles,
            )
        )

    def _get_volume_issue(self, issue_uri) -> str | None:
        volume = None
        volume_data = issue_uri.split("/")[-3].split("_")
        if volume_data[0] == "volume":
            volume = volume_data[1]
        return volume

    def _titles(self, pub_graph, uri):
        title: Literal
        for title in pub_graph.objects(rdflib.term.URIRef(uri), DCTERMS.title):
            yield Title(value=title.value, language=title.language)

    def _add_doi_identifier(self, doi: str):
        return ReferenceIdentifier(value=doi, type="doi")

    async def _document_type(self, pub_graph, uri):
        cache = {}
        document_type: Literal
        for document_type in pub_graph.objects(rdflib.term.URIRef(uri), RDF.type):
            if document_type in cache:
                yield cache[document_type]
                continue
            uri, label = SciencePlusDocumentTypeConverter().convert(str(document_type))
            document_type_db = await self._get_or_create_document_type_by_uri(
                uri, label
            )
            cache[document_type] = document_type_db
            yield document_type_db

    def _resolve_contributor(self, identifier: str):
        """
        For a given contributor identifier, return the URL to fetch the RDF data
        """
        if "http://www.idref.fr" in identifier:
            return identifier.replace("/id", ".rdf").replace("http://", "https://")
        if "http://hub.abes.fr" in identifier:
            return (
                "https://scienceplus.abes.fr/sparql?query="
                "define%20sql%3Adescribe-mode%20%22CBD%22%20%20"
                f"DESCRIBE%20%3C{identifier}%3E&output=xml"
            )
        raise ValueError(
            f"Unknown contributor identifier for Sciece Plus: {identifier}"
        )

    def _convert_role(self, role):
        return SciencePlusRolesConverter.convert(role)

    def _get_source(self):
        return "science_plus"

    def hash_keys(self, harvester_version: Version) -> list[HashKey]:
        return [
            HashKey(DCTERMS.title),
            HashKey(DCTERMS.abstract),
            HashKey(RDF.type),
        ]

    async def _query_ressource(self, uri):
        params = {
            "query": f'define sql:describe-mode "CBD"  DESCRIBE <{uri}>',
            "output": "application/rdf+xml",
        }
        # concatenate encoded params to query suffix
        query_uri = f"{self.SCIENCE_PLUS_QUERY_SUFFIX}?{urllib.parse.urlencode(params)}"
        client = RdfResolver(timeout=get_app_settings().idref_science_plus_timeout)
        return await client.fetch(query_uri, output_format="xml")
