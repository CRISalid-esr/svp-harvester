import aiohttp
from rdflib import SKOS, Graph
import rdflib
from app.services.concepts.concept_solver import ConceptSolver
from app.db.models.concept import Concept as DbConcept
from app.services.concepts.dereferencing_error import DereferencingError


class JelConceptSolver(ConceptSolver):
    """
    JEL concept solver
    """

    async def solve(self, concept_id: str) -> DbConcept:
        """
        Solves a JEL concept from a concept id
        :param concept_id: JEL code
        :return: Concept
        """
        uri, url = await self._build_url_from_concept_id_or_uri(concept_id)
        try:
            async with aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=float(2))
            ) as session:
                async with session.get(url) as response:
                    if not 200 <= response.status < 300:
                        raise DereferencingError(
                            f"Endpoint returned status {response.status} while dereferencing {uri}"
                        )
                    xml = (await response.text()).strip()
                    concept_graph = Graph().parse(data=xml, format="xml")
                    concept = DbConcept(uri=uri)
                    pref_labels = concept_graph.objects(
                        rdflib.URIRef(uri), SKOS.prefLabel
                    )
                    alt_labels = concept_graph.objects(
                        rdflib.URIRef(uri), SKOS.altLabel
                    )
                    self._add_labels(
                        concept=concept, labels=list(pref_labels), preferred=True
                    )
                    self._add_labels(
                        concept=concept, labels=list(alt_labels), preferred=False
                    )
                    return concept

        except Exception as error:
            raise DereferencingError(
                f"Unknown error while dereferencing JEL {uri} with message {error}"
            ) from error

    async def _build_url_from_concept_id_or_uri(self, concept_id: str):
        """
        Builds a URL from a JEL URI
        :param concept_id: Jel code
        :return: URI and URL
        """
        code = concept_id.split("#")[-1]
        uri = f"http://zbw.eu/beta/external_identifiers/jel#{code}"
        url = f"https://zbw.eu/beta/skosmos/rest/v1/jel/data?uri=http%3A%2F%2Fzbw.eu%2Fbeta%2Fexternal_identifiers%2Fjel%23{code}&format=application/rdf%2Bxml"
        return uri, url
