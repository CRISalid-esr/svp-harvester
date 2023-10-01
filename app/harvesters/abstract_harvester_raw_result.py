from dataclasses import dataclass
from typing import TypeVar, Generic

ResultTypeT = TypeVar('ResultTypeT')
IdentifierTypeT = TypeVar('IdentifierTypeT')


@dataclass(kw_only=True)
class AbstractHarvesterRawResult(Generic[IdentifierTypeT, ResultTypeT]):
    """
    Data class to store typical raw results from harvesters
    """

    # When an harvester may produce results from different sources,
    # in several formats, the formatter field is used to help
    # the converter to know how to handle the payload
    formatter_name: str

    # The source identifier may be an uri for semantic endpoints,
    # or a string for non-semantic endpoints
    source_identifier: IdentifierTypeT

    # for non-semantic endpoints, the payload is delivered as json and represented as a dict
    # for semantic endpoints, the payload is delivered as rdf and represented as a graph
    payload: ResultTypeT
