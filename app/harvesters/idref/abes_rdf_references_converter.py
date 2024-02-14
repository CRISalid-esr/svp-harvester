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

    @AbstractReferencesConverter.validate_reference
    async def convert(self, raw_data: RdfRawResult) -> Reference | None:
        new_ref = Reference()
        pub_graph: Graph = raw_data.payload
        uri = raw_data.source_identifier
        new_ref.source_identifier = str(uri)

        [  # pylint: disable=expression-not-assigned
            new_ref.titles.append(title) for title in self._titles(pub_graph, uri)
        ]

        [  # pylint: disable=expression-not-assigned
            new_ref.abstracts.append(abstract)
            for abstract in self._abstracts(pub_graph, uri)
        ]

        [  # pylint: disable=expression-not-assigned
            new_ref.identifiers.append(document_idenfier)
            for document_idenfier in self._add_reference_identifiers(pub_graph, uri)
        ]

        new_ref.hash = self._hash_from_rdf_graph(pub_graph, uri)
        return new_ref

    def _hash_from_rdf_graph(self, pub_graph: Graph, uri: str) -> str:
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
