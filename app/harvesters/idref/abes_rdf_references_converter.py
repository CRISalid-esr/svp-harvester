from abc import abstractmethod

import rdflib
from loguru import logger
from rdflib import FOAF, Graph, Literal, DCTERMS, Namespace

from app.db.models.abstract import Abstract
from app.db.models.book import Book
from app.db.models.reference import Reference
from app.db.models.reference_identifier import ReferenceIdentifier
from app.harvesters.abstract_references_converter import AbstractReferencesConverter
from app.harvesters.idref.rdf_resolver import RdfResolver
from app.harvesters.rdf_harvester_raw_result import (
    RdfHarvesterRawResult as RdfRawResult,
)


class AbesRDFReferencesConverter(AbstractReferencesConverter):
    """
    Converts raw data from ABES RDF to a normalised Reference object
    """

    async def convert(self, raw_data: RdfRawResult, new_ref: Reference) -> None:
        pub_graph: Graph = raw_data.payload
        uri = raw_data.source_identifier

        [  # pylint: disable=expression-not-assigned
            new_ref.titles.append(title) for title in self._titles(pub_graph, uri)
        ]

        [  # pylint: disable=expression-not-assigned
            new_ref.abstracts.append(abstract)
            for abstract in self._abstracts(pub_graph, uri)
        ]

        [  # pylint: disable=expression-not-assigned
            new_ref.identifiers.append(document_identifier)
            for document_identifier in self._add_reference_identifiers(pub_graph, uri)
        ]

        async for document_type in self._document_type(pub_graph, uri):
            new_ref.document_type.append(document_type)

        async for contribution in self._add_contributions(pub_graph, uri):
            new_ref.contributions.append(contribution)

        if "Article" in [dc.label for dc in new_ref.document_type]:
            async for biblio_graph, uri in self._get_bibliographic_resource(
                pub_graph=raw_data.payload, uri=raw_data.source_identifier
            ):
                if not biblio_graph or not uri:
                    continue
                journal = await self._get_journal(biblio_graph, uri)
                if not journal:
                    continue
                new_ref.issue = await self._get_issue(biblio_graph, uri, journal)

        if ("Book" in [dc.label for dc in new_ref.document_type]) or (
            "Chapter" in [dc.label for dc in new_ref.document_type]
        ):
            book = await self._get_book(pub_graph, uri)
            if book:
                new_ref.book = book

    # pylint: disable=unused-argument
    async def _get_book(self, pub_graph, uri) -> Book | None:
        return None

    # pylint: disable=unused-argument
    async def _get_bibliographic_resource(self, pub_graph, uri):
        yield None, None

    async def _get_issue(self, biblio_graph, uri, journal):
        raise NotImplementedError()

    async def _get_journal(self, biblio_graph, uri):
        raise NotImplementedError()

    @abstractmethod
    def _titles(self, pub_graph, uri):
        raise NotImplementedError()

    # pylint: disable=unused-argument
    def _add_reference_identifiers(self, pub_graph, uri):
        yield ReferenceIdentifier(value=uri, type="uri")

    def _abstracts(self, pub_graph, uri):
        abstract: Literal
        for abstract in pub_graph.objects(rdflib.term.URIRef(uri), DCTERMS.abstract):
            yield Abstract(value=abstract.value, language=abstract.language)

    @abstractmethod
    async def _document_type(self, pub_graph, uri):
        raise NotImplementedError()

    @abstractmethod
    def _convert_role(self, role):
        raise NotImplementedError()

    @abstractmethod
    def _resolve_contributor(self, identifier):
        raise NotImplementedError()

    @abstractmethod
    def _get_source(self):
        raise NotImplementedError()

    async def _add_contributions(self, pub_graph, uri):
        contribution_informations = []
        marcrel = Namespace("http://id.loc.gov/vocabulary/relators/")
        query = f"""
                        SELECT ?predicate ?object 
                        WHERE {{
                            ?subject ?predicate ?object .
                            FILTER(STRSTARTS(STR(?predicate), "{str(marcrel)}")).
                        }}
                    """
        results = pub_graph.query(query)
        for role, identifier in results:
            try:
                role = role.split("/")[-1]
                graph = await RdfResolver().fetch(self._resolve_contributor(identifier))
                contributor_name = ""
                for name in graph.objects(identifier, FOAF.name):
                    contributor_name = name
                contribution_informations.append(
                    AbstractReferencesConverter.ContributionInformations(
                        role=self._convert_role(role),
                        identifier=identifier,
                        name=contributor_name,
                        rank=None,
                    )
                )
            except ValueError as e:
                logger.warning(f"Error while fetching contributor: {e}")
                continue

        async for contribution in self._contributions(
            contribution_informations=contribution_informations,
            source=self._get_source(),
        ):
            yield contribution
