from abc import ABC
from typing import Generator

import rdflib
from aiohttp import ClientTimeout
from rdflib import SKOS, Graph, term
from rdflib.term import Node

from app.db.models.concept import Concept as DbConcept
from app.http.aio_http_client_manager import AioHttpClientManager
from app.services.concepts.concept_informations import ConceptInformations
from app.services.concepts.concept_solver import ConceptSolver
from app.services.errors.dereferencing_error import (
    handle_concept_dereferencing_error,
    DereferencingError,
)
from app.utilities.execution_timer_wrapper import execution_timer


class RdfConceptSolver(ConceptSolver, ABC):
    """
    Abstract mother class for concept solvers using RDF
    """

    @execution_timer
    @handle_concept_dereferencing_error
    async def solve(self, concept_informations: ConceptInformations) -> DbConcept:
        """
        Solves a RDF concept from a concept id
        :param concept_informations: concept informations
        :return: Concept
        """
        session = await AioHttpClientManager.get_session()
        request_timeout = ClientTimeout(total=float(self.timeout))

        async with session.get(
            concept_informations.url, timeout=request_timeout
        ) as response:
            if not 200 <= response.status < 300:
                await response.release()
                raise DereferencingError(
                    f"Endpoint returned status {response.status}"
                    f" while dereferencing RDF concept {concept_informations.uri}"
                    f" at url {concept_informations.url}"
                )

            xml = (await response.text()).strip()

        try:
            concept_graph = Graph().parse(data=xml, format="xml")
        except rdflib.exceptions.ParserError as error:
            raise DereferencingError(
                f"Error while parsing XML from {concept_informations.url} with message {error}"
            ) from error

        concept = DbConcept(uri=concept_informations.uri)

        self._add_labels(
            concept=concept,
            labels=list(self._pref_labels(concept_graph, concept_informations.uri)),
            preferred=True,
        )
        self._add_labels(
            concept=concept,
            labels=list(self._alt_labels(concept_graph, concept_informations.uri)),
            preferred=False,
        )

        return concept

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
