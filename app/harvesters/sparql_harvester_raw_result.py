from dataclasses import dataclass

from rdflib import URIRef

from app.harvesters.abstract_harvester_raw_result import AbstractHarvesterRawResult


@dataclass(kw_only=True)
class SparqlHarvesterRawResult(AbstractHarvesterRawResult[URIRef, dict]):
    """
    Raw result of an Harvester of a sparql endpoint
    with identifier as an URL and payload as a dict
    """
