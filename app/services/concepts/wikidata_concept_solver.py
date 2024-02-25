import json
import re
from typing import List

import aiohttp
from loguru import logger
from rdflib import Literal

from app.db.models.concept import Concept as DbConcept
from app.db.models.label import Label as DbLabel
from app.services.concepts.concept_informations import ConceptInformations
from app.services.concepts.concept_solver import ConceptSolver
from app.services.concepts.dereferencing_error import DereferencingError


class WikidataConceptSolver(ConceptSolver):
    """
    Wikidata concept solver
    """

    async def solve(self, concept_informations: ConceptInformations) -> DbConcept:
        """
        Solves a Wikidata concept from a concept id
        :param concept_informations: concept informations
        :return: Concept
        """
        try:
            async with aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=float(10))
            ) as session:
                async with session.get(concept_informations.url) as response:
                    if not 200 <= response.status < 300:
                        raise DereferencingError(
                            f"Endpoint returned status {response.status} "
                            f"while dereferencing Wikidata concept "
                            f"{concept_informations.uri} "
                            f"from url {concept_informations.url}"
                        )
                    json_response = await response.json()
                    concept_data: json = json_response["entities"][
                        concept_informations.code
                    ]
                    concept = DbConcept(uri=concept_informations.uri)

                    self._add_labels(
                        concept=concept,
                        labels=[
                            Literal(pair["value"], lang=pair["language"])
                            for language_value_pairs in self._alt_labels(
                                concept_data
                            ).values()
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

        except aiohttp.ClientError as error:
            logger.error(
                f"Endpoint failure while dereferencing {concept_informations.uri}"
                f"at url {concept_informations.url} with message {error}"
            )
            raise DereferencingError(
                f"Endpoint failure while dereferencing {concept_informations.uri}"
                f"at url {concept_informations.url} with message {error}"
            ) from error
        except Exception as error:
            logger.error(
                f"Exception failure dereferencing {concept_informations.uri}"
                f"at url {concept_informations.url} with message {error}"
            )
            raise DereferencingError(
                f"Exception failure dereferencing {concept_informations.uri}"
                f"at url {concept_informations.url} with message {error}"
            ) from error

    def _alt_labels(self, concept_data: json) -> List[str]:
        return concept_data.get("aliases", {})

    # pylint: disable=unused-argument
    def _pref_labels(self, concept_data: json) -> List[str]:
        return concept_data.get("labels", {})

    def _add_labels(self, concept: DbConcept, labels: dict, preferred: bool = True):
        def interesting_labels(label_language):
            a = (
                label_language in self.settings.concept_languages
                or label_language is None
            )
            return a

        if len(labels) == 0:
            return
        if preferred:
            preferred_labels = [
                labels[label_language]
                for label_language in labels
                if interesting_labels(label_language)
            ]
            for label in preferred_labels:
                self._add_label(concept, label, preferred)

        else:
            alt_labels = [
                labels[label_language][0]
                for label_language in labels
                if interesting_labels(label_language)
            ]
            for label in alt_labels:
                self._add_label(concept, label, preferred)

    def _add_label(self, concept, label, preferred):
        concept.labels.append(
            DbLabel(
                value=label["value"],
                language=label["language"],
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
