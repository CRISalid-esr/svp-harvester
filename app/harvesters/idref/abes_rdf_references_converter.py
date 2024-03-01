import hashlib
from abc import abstractmethod

import rdflib
from rdflib import Graph, Literal, DCTERMS

from app.db.models.abstract import Abstract
from app.db.models.reference_identifier import ReferenceIdentifier
from app.db.models.reference import Reference
from app.harvesters.abstract_references_converter import AbstractReferencesConverter
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
