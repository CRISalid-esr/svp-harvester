import hashlib

import rdflib
from rdflib import Graph, DC, Literal

from app.db.models.reference import Reference
from app.db.models.title import Title
from app.harvesters.abstract_references_converter import AbstractReferencesConverter
from app.harvesters.idref.idref_harvester import IdrefHarvester
from app.harvesters.rdf_harvester_raw_result import (
    RdfHarvesterRawResult as RdfRawResult,
)
from app.harvesters.sparql_harvester_raw_result import (
    SparqlHarvesterRawResult as SparqlRawResult,
)


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
            return self._convert_from_sudoc(raw_data)
        return None

    def _convert_from_sudoc(self, raw_data: RdfRawResult) -> Reference:
        new_ref = Reference()
        pub_graph: Graph = raw_data.payload
        uri = raw_data.source_identifier
        new_ref.source_identifier = uri
        [  # pylint: disable=expression-not-assigned
            new_ref.titles.append(title) for title in self._titles(pub_graph, uri)
        ]
        new_ref.hash = self._hash(pub_graph, uri)
        return new_ref

    def _hash(self, pub_graph: Graph, uri: str) -> str:
        graph_as_dict = {
            str(p): str(o)
            for s, p, o in pub_graph.triples((rdflib.term.URIRef(uri), None, None))
        }
        return hashlib.sha256(str(graph_as_dict).encode()).hexdigest()

    def _titles(self, pub_graph, uri):
        title: Literal
        for title in pub_graph.objects(rdflib.term.URIRef(uri), DC.title):
            value = title.value
            language = (
                title.language or "fr"  # TODO migrate to "default language" in config
            )
            yield Title(value=value, language=language)
