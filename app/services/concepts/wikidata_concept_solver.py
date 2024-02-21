import json
from typing import List, Tuple
import aiohttp
from loguru import logger
from app.db.models.concept import Concept as DbConcept
from app.db.models.label import Label as DbLabel
from app.services.concepts.concept_solver import ConceptSolver
from app.services.concepts.dereferencing_error import DereferencingError


class WikidataConceptSolver(ConceptSolver):
    """
    Wikidata concept solver
    """

    def get_uri(self, concept_id: str) -> str:
        """
        Get the uri of a concept from a concept id
        :param concept_id: concept id
        :return: uri
        """
        _, wikidata_uri = self._build_url_from_concept_id_or_uri(concept_id)
        return wikidata_uri

    async def solve(self, concept_id: str) -> DbConcept:
        """
        Solves a Wikidata concept from a concept id
        :param concept_id: concept id
        :return: Concept
        """
        wikidata_url, wikidata_uri = self._build_url_from_concept_id_or_uri(concept_id)
        try:
            async with aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=float(2))
            ) as session:
                async with session.get(wikidata_url) as response:
                    if not 200 <= response.status < 300:
                        raise DereferencingError(
                            "Endpoint returned status "
                            + f"{response.status} while dereferencing "
                            + f"{wikidata_uri}"
                        )
                    concept_data: json = (await response.json())["entities"][concept_id]
                    concept = DbConcept(uri=wikidata_uri)

                    [  # pylint: disable=expression-not-assigned
                        self._add_labels(
                            concept=concept, labels=label[0], preferred=label[1]
                        )
                        for label in self._get_labels(concept_data, wikidata_uri)
                    ]

                    return concept

        except aiohttp.ClientError as error:
            logger.error(
                f"Endpoint failure while dereferencing {wikidata_uri} with message {error}"
            )
            raise DereferencingError(
                f"Endpoint failure while dereferencing {wikidata_uri} with message {error}"
            ) from error
        except Exception as error:
            logger.error(
                f"Exception failure while dereferencing {wikidata_uri} with message {error}"
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

    def _build_url_from_concept_id_or_uri(self, concept_id: str) -> Tuple[str, str]:
        """
        Builds a URL from a Wikidata uri
        :param concept_id: concept id or uri
        :return: URL, URI
        """
        concept_id = concept_id.replace("https://www.wikidata.org/wiki/", "")

        wikidata_uri = f"http://www.wikidata.org/entity/{concept_id}"
        wikidata_url = (
            f"https://www.wikidata.org/wiki/Special:EntityData/{concept_id}.json"
        )

        return wikidata_url, wikidata_uri
