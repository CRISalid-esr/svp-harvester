import aiohttp
from rdflib import Graph
import rdflib
from app.db.models.concept import Concept as DbConcept
from app.services.concepts.concept_solver_rdf import ConceptSolverRdf
from app.services.concepts.dereferencing_error import DereferencingError


class JelConceptSolver(ConceptSolverRdf):
    """
    JEL concept solver
    """

    async def solve(self, concept_id: str) -> DbConcept:
        """
        Solves a JEL concept from a concept id
        :param concept_id: JEL code
        :return: Concept
        """
        uri, url = await self._build_url_from_concept_uri(concept_id)
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

                    [  # pylint: disable=expression-not-assigned
                        self._add_labels(
                            concept=concept, labels=list(label[0]), preferred=label[1]
                        )
                        for label in self._get_labels(concept_graph, uri)
                    ]

                    return concept
        except aiohttp.ClientError as error:
            raise DereferencingError(
                f"Endpoint failure while dereferencing {uri} with message {error}"
            ) from error
        except rdflib.exceptions.ParserError as error:
            raise DereferencingError(
                f"Error while parsing xml from {uri} with message {error}"
            ) from error
        except Exception as error:
            raise DereferencingError(
                f"Unknown error while dereferencing {uri} with message {error}"
            ) from error

    async def _build_url_from_concept_uri(self, uri: str):
        """
        Builds a URL from a JEL URI
        :param concept_id: Jel code
        :return: URI and URL
        """
        url = f"https://zbw.eu/beta/skosmos/rest/v1/jel/data?uri={uri}&format=application/rdf%2Bxml"
        return uri, url
