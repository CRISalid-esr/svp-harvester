from abc import ABC, abstractmethod
from typing import Generator

import aiohttp
import rdflib
from rdflib import SKOS, Graph, term
from rdflib.term import Node

from app.db.models.concept import Concept as DbConcept
from app.services.concepts.concept_solver import ConceptSolver
from app.services.concepts.dereferencing_error import DereferencingError


class RdfConceptSolver(ConceptSolver, ABC):
    """
    Abstract mother class for concept solvers using RDF
    """

    async def solve(self, concept_id: str) -> DbConcept:
        """
        Solves a RDF concept from a concept id
        :param concept_id: JEL code
        :return: Concept
        """
        uri, url = self._build_url_from_concept_uri(concept_id)
        try:
            async with aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=float(2))
            ) as session:
                async with session.get(url) as response:
                    if not 200 <= response.status < 300:
                        raise DereferencingError(
                            f"Endpoint returned status {response.status}"
                            f" while dereferencing {uri}"
                            f" at url {url}"
                        )
                    xml = (await response.text()).strip()
                    concept_graph = Graph().parse(data=xml, format="xml")
                    concept = DbConcept(uri=uri)

                    self._add_labels(
                        concept=concept,
                        labels=list(self._pref_labels(concept_graph, uri)),
                        preferred=True,
                    )
                    self._add_labels(
                        concept=concept,
                        labels=list(self._alt_labels(concept_graph, uri)),
                        preferred=False,
                    )
                    return concept
        except aiohttp.ClientError as error:
            raise DereferencingError(
                f"Endpoint failure while dereferencing {url} with message {error}"
            ) from error
        except rdflib.exceptions.ParserError as error:
            raise DereferencingError(
                f"Error while parsing xml from {url} with message {error}"
            ) from error
        except Exception as error:
            raise DereferencingError(
                f"Unknown error while dereferencing {url} with message {error}"
            ) from error

    def _get_labels(
        self, concept_data: Graph, uri: str, label_type: term.URIRef
    ) -> Generator[Node, None, None]:
        """
        Get labels from a concept graph based on the given label type
        :param concept_data: concept graph
        :param uri: concept uri
        :param label_type: SKOS prefLabel or altLabel

        :return: labels
        """
        return concept_data.objects(term.URIRef(uri), label_type)

    def _pref_labels(
        self, concept_data: Graph, uri: str
    ) -> Generator[Node, None, None]:
        """
        Get preferred labels from a concept graph
        :param concept_data: concept graph
        :param uri: concept uri

        :return: preferred labels
        """
        return self._get_labels(concept_data, uri, SKOS.prefLabel)

    def _alt_labels(self, concept_data: Graph, uri: str) -> Generator[Node, None, None]:
        """
        Get alternative labels from a concept graph
        :param concept_data: concept graph
        :param uri: concept uri

        :return: alternative labels
        """
        return self._get_labels(concept_data, uri, SKOS.altLabel)

    @abstractmethod
    def _build_url_from_concept_uri(self, concept_id):
        pass
