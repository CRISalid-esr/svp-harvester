import rdflib
from rdflib import DC, DCTERMS, Graph, Literal, Namespace

from app.db.models.book import Book
from app.db.models.issue import Issue
from app.db.models.journal import Journal
from app.db.models.reference import Reference
from app.db.models.title import Title
from app.harvesters.abstract_references_converter import AbstractReferencesConverter
from app.harvesters.exceptions.unexpected_format_exception import (
    UnexpectedFormatException,
)
from app.harvesters.idref.abes_rdf_references_converter import (
    AbesRDFReferencesConverter,
)
from app.harvesters.idref.rdf_resolver import RdfResolver
from app.harvesters.idref.sudoc_document_type_converter import (
    SudocDocumentTypeConverter,
)
from app.harvesters.rdf_harvester_raw_result import RdfHarvesterRawResult
from app.harvesters.idref.sudoc_qualities_converter import SudocQualitiesConverter
from app.services.book.book_data_class import BookInformations
from app.services.hash.hash_key import HashKey
from app.services.issue.issue_data_class import IssueInformations
from app.services.journal.journal_data_class import JournalInformations
from app.utilities.isbn_utilities import get_isbns
from app.utilities.string_utilities import normalize_string, remove_after_separator


class SudocReferencesConverter(AbesRDFReferencesConverter):
    """
    Converts raw data from Sudoc to a normalised Reference object
    """

    RDF_BIBO = Namespace("http://purl.org/ontology/bibo/")
    FABIO_NAMESPACE = Namespace("http://purl.org/spar/fabio/")
    RDAU = Namespace("http://rdaregistry.info/Elements/u/")

    @AbesRDFReferencesConverter.validate_reference
    async def convert(
        self, raw_data: RdfHarvesterRawResult, new_ref: Reference
    ) -> None:
        await super().convert(raw_data=raw_data, new_ref=new_ref)
        if not new_ref.titles:
            raise UnexpectedFormatException(
                f"Sudoc reference without title: {new_ref.source_identifier}"
            )

        # If we have an article, we need to get the journal and issue
        if "Article" in [dc.label for dc in new_ref.document_type]:
            async for biblio_graph, uri in self._get_bibliographic_resource(
                pub_graph=raw_data.payload, uri=raw_data.source_identifier
            ):
                journal = await self._get_journal(biblio_graph, uri)
                issue = await self._get_issue(
                    journal=journal, biblio_graph=biblio_graph, uri=uri
                )
                new_ref.issue = issue

    def _harvester(self) -> str:
        return "Idref"

    async def _get_book(self, pub_graph, uri) -> Book | None:
        isbn10 = None
        isbn13_from_isbn10 = None
        for isbn10 in pub_graph.objects(rdflib.term.URIRef(uri), self.RDF_BIBO.isbn10):
            isbn10 = isbn10.value
        if isbn10:
            isbn10, isbn13_from_isbn10 = get_isbns(isbn10)
        isbn13 = None
        for isbn13 in pub_graph.objects(rdflib.term.URIRef(uri), self.RDF_BIBO.isbn13):
            isbn13 = isbn13.value
        if not isbn13 and isbn13_from_isbn10:
            isbn13 = isbn13_from_isbn10
        else:
            _, isbn13 = get_isbns(isbn13)

        publisher: Literal
        for publisher in pub_graph.objects(rdflib.term.URIRef(uri), DC.publisher):
            publisher = publisher.value
        title = None
        for title in pub_graph.objects(rdflib.term.URIRef(uri), DC.title):
            title = title.value
        return await self._get_or_create_book(
            BookInformations(
                title=title,
                isbn10=isbn10,
                isbn13=isbn13,
                publisher=publisher,
            )
        )

    async def _get_bibliographic_resource(self, pub_graph, uri) -> Graph:
        document: Literal
        for document in pub_graph.objects(rdflib.term.URIRef(uri), DCTERMS.isPartOf):
            document_uri = str(document)
            document = str(document).replace("/id", ".rdf")
            document = document.replace("http", "https")
            document_graph = await RdfResolver().fetch(document)
            yield document_graph, document_uri
            # We only want the first appearance.
            break

    async def _get_issue(self, biblio_graph, uri, journal) -> Issue:
        source_identifier = normalize_string("-".join(journal.titles)) + "-sudoc"
        return await self._get_or_create_issue(
            IssueInformations(
                source="sudoc", source_identifier=source_identifier, journal=journal
            )
        )

    async def _get_journal(self, biblio_graph, uri) -> Journal:
        titles = []
        issn_value = []
        for issn in biblio_graph.objects(rdflib.term.URIRef(uri), self.RDF_BIBO.issn):
            issn_value.append(issn.value)
        issn_l_value = None
        for issn_l in biblio_graph.objects(
            rdflib.term.URIRef(uri), self.FABIO_NAMESPACE.hasIssnL
        ):
            issn_l_value = issn_l.value
        title_value = None
        for title in biblio_graph.objects(rdflib.term.URIRef(uri), DC.title):
            title_value = title.value
        if title_value is not None:
            titles.append(title_value)
        title_key_value = None
        for title_key in biblio_graph.objects(
            rdflib.term.URIRef(uri), self.RDAU.P60597
        ):
            title_key_value = title_key.value
        if title_key_value is not None:
            titles.append(title_key_value)
        publisher_value = None
        for publisher in biblio_graph.objects(rdflib.term.URIRef(uri), DC.publisher):
            publisher_value = publisher.value
            # We only want the first appearance.
            break
        return await self._get_or_create_journal(
            JournalInformations(
                source="sudoc",
                source_identifier=uri,
                issn=issn_value,
                issn_l=issn_l_value,
                publisher=publisher_value,
                titles=titles,
            )
        )

    def _titles(self, pub_graph, uri):
        title: Literal
        for title in pub_graph.objects(rdflib.term.URIRef(uri), DC.title):
            yield Title(
                value=remove_after_separator(title.value, "/"), language=title.language
            )

    async def _document_type(self, pub_graph, uri):
        for document_type in pub_graph.objects(
            rdflib.term.URIRef(uri), rdflib.RDF.type
        ):
            uri, label = SudocDocumentTypeConverter().convert(str(document_type))
            yield await self._get_or_create_document_type_by_uri(uri, label)

    async def _add_contributions(self, pub_graph, uri):
        contribution_informations = []
        query = """
                    PREFIX foaf: <http://xmlns.com/foaf/0.1/>
                    PREFIX marcrel: <http://id.loc.gov/vocabulary/relators/>

                    SELECT DISTINCT ?role ?person ?name
                    WHERE {
                        ?work ?role ?person .
                        ?person a foaf:Person .
                        ?person foaf:name ?name .
                        FILTER(STRSTARTS(STR(?role), STR(marcrel:)))
                    }
                """

        results = pub_graph.query(query)
        for role, identifier, name in results:
            role = role.split("/")[-1]
            contribution_informations.append(
                AbstractReferencesConverter.ContributionInformations(
                    role=self._convert_role(role),
                    identifier=str(identifier),
                    name=str(name),
                    rank=None,
                )
            )

        async for contribution in self._contributions(
            contribution_informations=contribution_informations,
            source=self._get_source(),
        ):
            yield contribution

    def _get_source(self):
        return "sudoc"

    def _resolve_contributor(self, identifier):
        pass

    def _convert_role(self, role):
        return SudocQualitiesConverter.convert(role)

    def hash_keys(self):
        return [
            HashKey(DC.title),
            HashKey(DC.type),
            HashKey(DCTERMS.abstract),
        ]
