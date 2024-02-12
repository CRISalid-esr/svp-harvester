from dataclasses import dataclass

from rdflib import Graph, URIRef

from app.harvesters.abstract_harvester_raw_result import AbstractHarvesterRawResult


@dataclass(kw_only=True)
class RdfHarvesterRawResult(AbstractHarvesterRawResult[URIRef, Graph]):
    """
    Raw result of an Harvester with identifier as an URL and payload as a graph
    """

    doi: str = None
