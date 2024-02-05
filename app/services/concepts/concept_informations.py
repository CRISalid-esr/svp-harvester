from dataclasses import dataclass
from enum import Enum


@dataclass
class ConceptInformations:
    """
    Concept informations is a dataclass encapsulating language, uri, value, and source of a concept
    """

    class ConceptSources(Enum):
        """
        Closed list of supported sources
        """

        IDREF = "IDREF"
        WIKIDATA = "WIKIDATA"
        # add more sources here

    language: str | None = None
    uri: str | None = None
    label: str | None = None
    source: ConceptSources | None = None
