import urllib
from typing import Generator

from rdflib import Graph, RDFS
from rdflib.term import Node

from app.services.concepts.concept_informations import ConceptInformations
from app.services.concepts.dereferencing_error import DereferencingError
from app.services.concepts.rdf_concept_solver import RdfConceptSolver


class AbesConceptSolver(RdfConceptSolver):
    """
    ABES concept solver
    """

    def complete_information(self, concept_informations: ConceptInformations) -> None:
        """
        Build url, code and/or uri from concept informations
        """
        if concept_informations.uri is not None:
            url = (
                "https://scienceplus.abes.fr/sparql?"
                "query=define%20sql%3Adescribe-mode%20%22CBD%22%20%20DESCRIBE%20%3C"
                f"{urllib.parse.quote(concept_informations.uri)}"
                "%3E&output=application%2Frdf%2Bxml"
            )
            concept_informations.url = url
        else:
            raise DereferencingError(
                "Unable to build required fields to solve Abes concept"
                f"from information : {concept_informations}"
            )

    def _pref_labels(
        self, concept_data: Graph, uri: str
    ) -> Generator[Node, None, None]:
        return self._get_labels(concept_data, uri, RDFS.label)
