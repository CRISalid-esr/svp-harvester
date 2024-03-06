from rdflib import Graph
import rdflib
from app.harvesters.rdf_harvester_raw_result import RdfHarvesterRawResult
from app.services.hash.asbtract_hash_generator import AbstractHashGenerator


class RdfHashGenerator(AbstractHashGenerator):
    """
    Hasher for RdfHarvesterRawResult
    """

    def hash_string(self, raw_data: RdfHarvesterRawResult, hash_keys: dict) -> str:
        uri: str = raw_data.source_identifier
        pub_graph: Graph = raw_data.payload
        hash_string = ""
        for predicate in hash_keys:
            objects = self._get_objects(pub_graph, uri, predicate)
            hash_string += ";".join(sorted([str(o) for o in objects]))

        return str(hash_string)

    def _get_objects(self, pub_graph: Graph, uri: str, predicate):
        return pub_graph.objects(rdflib.term.URIRef(uri), predicate)
