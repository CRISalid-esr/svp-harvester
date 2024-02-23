import urllib

from app.services.concepts.rdf_concept_solver import RdfConceptSolver
from app.services.concepts.jel_concept_solver import JelConceptSolver


class SkosmosJelConceptSolver(JelConceptSolver, RdfConceptSolver):
    """
    JEL concept solver
    """

    def _build_url_from_concept_uri(self, uri: str):
        """
        Builds Skosmos URL from a JEL URI
        :param uri: JEL URI
        :return: URI and URL
        """
        url = f"https://zbw.eu/beta/skosmos/rest/v1/jel/data?uri={urllib.parse.quote(uri)}&format=application/rdf%2Bxml"
        return uri, url
