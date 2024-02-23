import urllib
from typing import Tuple

from app.services.concepts.jel_concept_solver import JelConceptSolver
from app.services.concepts.rdf_concept_solver import RdfConceptSolver


class SkosmosJelConceptSolver(JelConceptSolver, RdfConceptSolver):
    """
    JEL concept solver
    """

    def _build_uri_and_url(self, concept_id_or_uri: str) -> Tuple[str, str]:
        """
        Builds Skosmos URL from a JEL URI
        :param uri: JEL URI
        :return: URI and URL
        """
        url = f"https://zbw.eu/beta/skosmos/rest/v1/jel/data?uri={urllib.parse.quote(concept_id_or_uri)}&format=application/rdf%2Bxml"
        return concept_id_or_uri, url
