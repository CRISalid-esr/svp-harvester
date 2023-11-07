import hashlib

import rdflib
from rdflib import Graph, DC, Literal, DCTERMS

from app.db.models.abstract import Abstract
from app.db.models.reference import Reference
from app.db.models.title import Title
from app.harvesters.abstract_references_converter import AbstractReferencesConverter
from app.harvesters.rdf_harvester_raw_result import (
    RdfHarvesterRawResult as RdfRawResult,
)


class SudocReferencesConverter(AbstractReferencesConverter):
    """
    Converts raw data from Sudoc to a normalised Reference object
    """

    async def convert(self, raw_data: RdfRawResult) -> Reference:
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
        new_ref.hash = self._hash_from_rdf_graph(pub_graph, uri)
        return new_ref

    def _hash_from_rdf_graph(self, pub_graph: Graph, uri: str) -> str:
        graph_as_dict = {
            str(p): str(o)
            for s, p, o in pub_graph.triples((rdflib.term.URIRef(uri), None, None))
        }
        return hashlib.sha256(str(graph_as_dict).encode()).hexdigest()

    def _titles(self, pub_graph, uri):
        title: Literal
        for title in pub_graph.objects(rdflib.term.URIRef(uri), DC.title):
            yield Title(value=title.value, language=title.language)

    def _abstracts(self, pub_graph, uri):
        abstract: Literal
        for abstract in pub_graph.objects(rdflib.term.URIRef(uri), DCTERMS.abstract):
            yield Abstract(value=abstract.value, language=abstract.language)
