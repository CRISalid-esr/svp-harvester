import aiohttp
from loguru import logger
from rdflib import SKOS, Graph
import rdflib
from app.services.concepts.concept_solver import ConceptSolver
from app.db.models.concept import Concept as DbConcept
from app.services.concepts.dereferencing_error import DereferencingError


class WikidataConceptSolver(ConceptSolver):
    """
    Wikidata concept solver
    """

    async def solve(self, concept_id: str) -> DbConcept:
        """
        Solves a Wikidata concept from a concept id
        :param concept_id: concept id
        :return: Concept
        """
        wikidata_url, wikidata_uri = await self._build_url_from_concept_id_or_uri(
            concept_id
        )
        try:
            async with aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=float(10))
            ) as session:
                async with session.get(wikidata_url) as response:
                    if not 200 <= response.status < 300:
                        raise DereferencingError(
                            f"Endpoint returned status {response.status} while dereferencing {wikidata_uri}"
                        )
                    xml = (await response.text()).strip()
                    concept_graph = Graph().parse(data=xml)
                    concept = DbConcept(uri=concept_id)
                    # See if there is a owl:sameAs concept in the graph, if so, use it
                    same_as = concept_graph.objects(
                        rdflib.term.URIRef(wikidata_uri), rdflib.OWL.sameAs
                    )
                    new_concept_id = None
                    for same in same_as:
                        logger.warning(f"{concept_id} is the same as {same}")
                        new_concept_id = str(same)
                        break
                    if new_concept_id:
                        _, wikidata_uri = await self._build_url_from_concept_id_or_uri(
                            new_concept_id
                        )

                    pref_labels = concept_graph.objects(
                        rdflib.term.URIRef(wikidata_uri), SKOS.prefLabel
                    )
                    alt_labels = concept_graph.objects(
                        rdflib.term.URIRef(wikidata_uri), SKOS.altLabel
                    )
                    self._add_labels(
                        concept=concept, labels=list(pref_labels), preferred=True
                    )
                    self._add_labels(
                        concept=concept, labels=list(alt_labels), preferred=False
                    )

                    return concept

        except aiohttp.ClientError as error:
            raise DereferencingError(
                f"Endpoint failure while dereferencing {wikidata_uri} with message {error}"
            ) from error
        except rdflib.exceptions.ParserError as error:
            logger.warning(f"error: {error}")
            raise DereferencingError(
                f"Error while parsing xml from {wikidata_uri} with message {error}"
            ) from error
        except Exception as error:
            raise DereferencingError(
                f"Unknown error while dereferencing {wikidata_uri} with message {error}"
            ) from error

    async def _build_url_from_concept_id_or_uri(self, concept_id: str):
        """
        Builds a URL from a Wikidata uri
        :param concept_id: concept id or uri
        :return: URL, URI
        """
        concept_id = concept_id.replace("https://www.wikidata.org/wiki/", "")

        wikidata_uri = f"http://www.wikidata.org/entity/{concept_id}"
        wikidata_url = (
            f"https://www.wikidata.org/wiki/Special:EntityData/{concept_id}.ttl"
        )

        return wikidata_url, wikidata_uri
