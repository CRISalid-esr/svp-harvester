from typing import AsyncGenerator

import rdflib
from rdflib import DCTERMS, RDF, Literal, Namespace, URIRef

from app.db.models.document_type import DocumentType
from app.db.models.reference import Reference
from app.db.models.reference_identifier import ReferenceIdentifier
from app.db.models.title import Title
from app.harvesters.idref.abes_rdf_references_converter import (
    AbesRDFReferencesConverter,
)
from app.harvesters.idref.persee_qualities_converter import PerseeQualitiesConverter
from app.harvesters.rdf_harvester_raw_result import RdfHarvesterRawResult
from app.services.hash.hash_key import HashKey
from app.harvesters.idref.rdf_resolver import RdfResolver
from app.services.issue.issue_data_class import IssueInformations
from app.services.journal.journal_data_class import JournalInformations


class PerseeReferencesConverter(AbesRDFReferencesConverter):
    """
    Converts raw data from Persee to a normalised Reference object
    """

    RDF_BIBO = "http://purl.org/ontology/bibo/"

    def _harvester(self) -> str:
        return "Idref"

    @AbesRDFReferencesConverter.validate_reference
    async def convert(
        self, raw_data: RdfHarvesterRawResult, new_ref: Reference
    ) -> None:
        await super().convert(raw_data=raw_data, new_ref=new_ref)
        new_ref.page = self._page(raw_data.payload, raw_data.source_identifier)

    def _page(self, pub_graph, uri):
        page = ""
        for page_start in pub_graph.objects(
            rdflib.term.URIRef(uri), Namespace(self.RDF_BIBO).pageStart
        ):
            page += page_start.value
        for page_start in pub_graph.objects(
            rdflib.term.URIRef(uri), Namespace(self.RDF_BIBO).pageEnd
        ):
            page += "-" + page_start.value
        return page if page else None

    async def _get_journal(self, biblio_graph, uri):
        # Check we are dealing with an issue in the first place
        label_type = []
        for document_type_uri in biblio_graph.objects(
            rdflib.term.URIRef(uri), RDF.type
        ):
            label = str(document_type_uri).rsplit("/", maxsplit=1)[-1]
            label_type.append(label)
        if "Issue" not in label_type:
            return None

        titles = []

        issn_value = []
        for issn in biblio_graph.objects(
            rdflib.term.URIRef(uri), Namespace(self.RDF_BIBO).issn
        ):
            try:
                issn_value.append(issn.value)
            except AttributeError:
                issn_value.append(str(issn).rsplit("/", maxsplit=1)[-1])
        title_value = None
        for title in biblio_graph.objects(rdflib.term.URIRef(uri), DCTERMS.title):
            title_value = title.value
        if title_value is not None:
            titles.append(title_value)

        publisher_value = None
        for publisher in biblio_graph.objects(
            rdflib.term.URIRef(uri), DCTERMS.publisher
        ):
            publisher_value = publisher.value

        source_identifier = (
            f"{'-'.join(titles)}-{'-'.join(issn_value)}-{publisher_value}-persee"
        )
        return await self._get_or_create_journal(
            JournalInformations(
                source="sudoc",
                source_identifier=source_identifier,
                issn=issn_value,
                publisher=publisher_value,
                titles=titles,
            )
        )

    async def _get_issue(self, biblio_graph, uri, journal):
        source_identifier = uri
        number = None
        for number in biblio_graph.objects(
            rdflib.term.URIRef(uri), Namespace(self.RDF_BIBO).issue
        ):
            number = number.value
            break
        volume = None
        for volume in biblio_graph.objects(
            rdflib.term.URIRef(uri), Namespace(self.RDF_BIBO).volume
        ):
            volume = volume.value
            break
        return await self._get_or_create_issue(
            IssueInformations(
                source="persee",
                source_identifier=source_identifier,
                journal=journal,
                number=number,
                volume=volume,
            )
        )

    async def _get_bibliographic_resource(self, pub_graph, uri):
        document: Literal
        for document in pub_graph.objects(rdflib.term.URIRef(uri), DCTERMS.isPartOf):
            document_uri = str(document).replace("#Web", "#Print")
            document = str(document).replace("#Web", "")
            document = document.replace("http", "https")
            document_graph = await RdfResolver().fetch(document)
            yield document_graph, document_uri
            break

    def _add_reference_identifiers(self, pub_graph, uri):
        yield ReferenceIdentifier(value=uri, type="uri")
        for identifier in pub_graph.objects(
            rdflib.term.URIRef(uri), URIRef(self.RDF_BIBO + "doi")
        ):
            yield ReferenceIdentifier(value=identifier, type="doi")

    def _resolve_contributor(self, identifier):
        return identifier

    def _convert_role(self, role):
        return PerseeQualitiesConverter.convert(role)

    def _get_source(self):
        return "persee"

    async def _document_type(
        self, pub_graph, uri
    ) -> AsyncGenerator[DocumentType, None]:
        document_type_cache = {}
        document_type_uri: URIRef
        for document_type_uri in pub_graph.objects(rdflib.term.URIRef(uri), RDF.type):
            label = str(document_type_uri).rsplit("/", maxsplit=1)[-1]
            document_type_key = (document_type_uri, label)
            if document_type_key in document_type_cache:
                yield document_type_cache[document_type_key]
                continue

            document_type_db = await self._get_or_create_document_type_by_uri(
                uri=document_type_uri, label=label
            )
            document_type_cache[document_type_key] = document_type_db
            yield document_type_db

    def _titles(self, pub_graph, uri):
        title: Literal
        for title in pub_graph.objects(rdflib.term.URIRef(uri), DCTERMS.title):
            lng = title.language
            if not title.language:
                for lng in pub_graph.objects(rdflib.term.URIRef(uri), DCTERMS.language):
                    lng = lng.value
                    break
            yield Title(value=title.value, language=lng)

    def hash_keys(self) -> list[str]:
        return [
            HashKey(RDF.type),
            HashKey(DCTERMS.title),
            HashKey(DCTERMS.abstract),
        ]
