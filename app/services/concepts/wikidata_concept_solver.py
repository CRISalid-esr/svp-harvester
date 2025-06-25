import json
import re
from typing import List

from aiohttp import ClientTimeout
from rdflib import Literal

from app.db.models.concept import Concept as DbConcept
from app.db.models.label import Label as DbLabel
from app.http.aio_http_client_manager import AioHttpClientManager
from app.services.concepts.concept_informations import ConceptInformations
from app.services.concepts.concept_solver import ConceptSolver
from app.services.errors.dereferencing_error import (
    handle_concept_dereferencing_error,
    DereferencingError,
)


class WikidataConceptSolver(ConceptSolver):
    """
    Wikidata concept solver
    """

    @handle_concept_dereferencing_error
    async def solve(self, concept_informations: ConceptInformations) -> DbConcept:
        """
        Solves a Wikidata concept from a concept id
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
                    f"Endpoint returned status {response.status} "
                    f"while dereferencing Wikidata concept "
                    f"{concept_informations.uri} "
                    f"from url {concept_informations.url}"
                )
            json_response = await response.json()

        concept_data = json_response["entities"].get(concept_informations.code)

        if concept_data is None and len(json_response["entities"]) == 1:
            concept_data = list(json_response["entities"].values())[0]

        concept = DbConcept(uri=concept_informations.uri)

        self._add_labels(
            concept=concept,
            labels=[
                Literal(pair["value"], lang=pair["language"])
                for language_value_pairs in self._alt_labels(concept_data).values()
                for pair in language_value_pairs
            ],
            preferred=False,
        )
        self._add_labels(
            concept=concept,
            labels=[
                Literal(pair["value"], lang=pair["language"])
                for pair in self._pref_labels(concept_data).values()
            ],
            preferred=True,
        )
        return concept

    def _alt_labels(self, concept_data: json) -> List[str]:
        return concept_data.get("aliases", {})

    def _pref_labels(self, concept_data: json) -> List[str]:
        return concept_data.get("labels", {})

    def _add_labels(
        self, concept: DbConcept, labels: list[Literal], preferred: bool = True
    ):
        def interesting_languages(language):
            return language in self.settings.concept_languages or language is None

        if len(labels) == 0:
            return
        if preferred:
            preferred_labels = [
                label for label in labels if interesting_languages(label.language)
            ]
            for label in preferred_labels:
                self._add_label(concept, label, preferred)

        else:
            alt_labels = [
                label for label in labels if interesting_languages(label.language)
            ]
            for label in alt_labels:
                self._add_label(concept, label, preferred)

    def _add_label(self, concept: DbConcept, label: Literal, preferred: bool):
        concept.labels.append(
            DbLabel(
                value=label.value,
                language=label.language,
                preferred=preferred,
            )
        )

    def complete_information(
        self,
        concept_informations: ConceptInformations,
    ) -> None:
        """
        Ensure uri/code consistency and set URL
        :param concept_informations: concept informations
        :return: None
        """
        if concept_informations.code is None and concept_informations.uri is None:
            raise DereferencingError(
                f"Neither code nor uri provided for {concept_informations}"
            )
        if concept_informations.uri is not None:
            concept_informations.code = re.sub(
                r"https?://www.wikidata.org/(wiki|entity)/",
                "",
                concept_informations.uri,
            )
        if concept_informations.code is not None:
            concept_informations.uri = (
                f"http://www.wikidata.org/entity/{concept_informations.code}"
            )
        assert (
            concept_informations.uri is not None
        ), "Concept URI should not be None at this point"
        assert (
            concept_informations.code is not None
        ), "Concept code should not be None at this point"
        concept_informations.url = (
            "https://www.wikidata.org/wiki/Special:EntityData/"
            f"{concept_informations.code}.json"
        )
