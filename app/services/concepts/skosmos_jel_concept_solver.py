import urllib
from typing import Tuple

from app.services.concepts.concept_informations import ConceptInformations
from app.services.concepts.jel_concept_solver import JelConceptSolver
from app.services.concepts.rdf_concept_solver import RdfConceptSolver


class SkosmosJelConceptSolver(JelConceptSolver, RdfConceptSolver):
    """
    JEL concept solver
    """

    def complete_information(self, concept_informations: ConceptInformations) -> None:
        """
        Builds Skosmos URL from a JEL URI
        :param uri: JEL URI
        :return: URI and URL
        """
        super().complete_information(concept_informations)
        url = (
            "https://zbw.eu/beta/skosmos/rest/v1/jel/data?uri="
            f"{urllib.parse.quote(concept_informations.uri)}"
            "&format=application/rdf%2Bxml"
        )
        concept_informations.url = url
