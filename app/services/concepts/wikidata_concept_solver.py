import json
import re
from typing import List, Tuple
import aiohttp
from loguru import logger
from app.db.models.concept import Concept as DbConcept
from app.db.models.label import Label as DbLabel
from app.services.concepts.concept_informations import ConceptInformations
from app.services.concepts.concept_solver import ConceptSolver
from app.services.concepts.dereferencing_error import DereferencingError


class WikidataConceptSolver(ConceptSolver):
    """
    Wikidata concept solver
    """

    def add_uri(self, concept_informations: ConceptInformations) -> str:
        """
        Get the uri of a concept from a concept id
        :param concept_id: concept id
        :return: uri
        """
        self._build_url_from_concept_id_or_uri(concept_informations)

    async def solve(self, concept_informations: ConceptInformations) -> DbConcept:
        """
        Solves a Wikidata concept from a concept id
        :param concept_informations: concept informations
        :return: Concept
        """
        self._build_url_from_concept_id_or_uri(concept_informations)
        try:
            async with aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=float(2))
            ) as session:
                async with session.get(concept_informations.url) as response:
                    if not 200 <= response.status < 300:
                        raise DereferencingError(
                            "Endpoint returned status "
                            f"{response.status} while dereferencing "
                            f"{concept_informations.uri} "
                            f"at url {concept_informations.url}"
                        )
                    json_response = await response.json()
                    concept_data: json = json_response["entities"][
                        concept_informations.code
                    ]
                    concept = DbConcept(uri=concept_informations.uri)

                    [  # pylint: disable=expression-not-assigned
                        self._add_labels(
                            concept=concept, labels=label[0], preferred=label[1]
                        )
                        for label in self._get_labels(
                            concept_data, concept_informations.uri
                        )
                    ]

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
                f"Unknown error while dereferencing {wikidata_uri} with message {error}"
            ) from error

    # pylint: disable=unused-argument
    def _get_labels(self, concept_data: json, uri: str) -> List[Tuple[str, bool]]:
        pref_labels = concept_data.get("labels", {})
        alt_labels = concept_data.get("aliases", {})
        return [(pref_labels, True), (alt_labels, False)]

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

    @staticmethod
    def _build_url_from_concept_id_or_uri(
        cls, concept_informations: ConceptInformations
    ) -> None:
        """
        Builds a URL from a Wikidata uri
        :param concept_id: concept id or uri
        :return: URL, URI
        """
        if concept_informations.uri:
            concept_informations.code = re.sub(
                r"https?://www.wikidata.org/(wiki|entity)/",
                "",
                concept_informations.uri,
            )
        if concept_informations.code is None:
            raise DereferencingError(
                f"Unable to use wikidata concept informations {concept_informations.uri} {concept_informations.label}"
            )
        concept_informations.uri = (
            f"http://www.wikidata.org/entity/{concept_informations.code}"
        )
        concept_informations.url = f"https://www.wikidata.org/wiki/Special:EntityData/{concept_informations.code}.json"
