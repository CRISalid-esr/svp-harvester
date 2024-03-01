import hashlib
from abc import abstractmethod
from loguru import logger

import rdflib
from rdflib import FOAF, Graph, Literal, DCTERMS, Namespace

from app.db.models.abstract import Abstract
from app.db.models.reference_identifier import ReferenceIdentifier
from app.db.models.reference import Reference
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
            
        new_ref.harvester = "Idref.Abes"
        async for contribution in self._add_contributions(pub_graph, uri):
            new_ref.contributions.append(contribution)

        new_ref.hash = self._hash_from_rdf_graph(pub_graph, uri)
        return new_ref

    def hash(self, raw_data: RdfRawResult) -> str:
        pub_graph: Graph = raw_data.payload
        uri = raw_data.source_identifier
        graph_as_dict = {
            str(p): str(o)
            for s, p, o in pub_graph.triples((rdflib.term.URIRef(uri), None, None))
        }
        return hashlib.sha256(str(graph_as_dict).encode()).hexdigest()

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
