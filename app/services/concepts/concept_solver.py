from abc import ABC, abstractmethod

import rdflib

from app.config import get_app_settings
from app.db.models.concept import Concept as DbConcept
from app.db.models.label import Label as DbLabel


class ConceptSolver(ABC):
    """
    Abstract mother class for concept solvers
    """

    # fetch app settings in constructor
    def __init__(self):
        self.settings = get_app_settings()

    @abstractmethod
    async def get_uri(self, concept_id: str) -> str:
        """
        Get the uri of a concept from a concept id
        :param concept_id: concept id
        :return: uri
        """

    @abstractmethod
    async def solve(self, concept_id: str) -> DbConcept:
        """
        Solves a concept from a concept id
        :param concept_id: concept id
        :return: Concept
        """

    @abstractmethod
    def _get_labels(self, concept_data, uri: str):
        """
        Get labels from a concept graph
        :param concept_data: concept graph
        :param uri: concept uri
        :return: labels
        """

    def _add_labels(
        self,
        concept: DbConcept,
        labels: list[rdflib.term.Literal],
        preferred: bool = True,
    ):
        def interesting_labels(label):
            return (
                label.language in self.settings.concept_languages
                or label.language is None
            )

        if len(labels) == 0:
            return
        # If there is only one preflabel, add it
        # If there are several preflabels, and one one them
        # is in self.settings.concept_languages or has no language,
        # add only preflabels whose language is in self.settings.concept_languages
        # and preflabels whithout language
        # If there are several preflabels, and none of them
        # is in self.settings.concept_languages or has no language,
        # add the first one in any language
        if preferred:
            preferred_labels = [label for label in labels if interesting_labels(label)]
            for label in preferred_labels or [labels[0]]:
                self._add_label(concept, label, preferred)
        # Add all altlabels whose language is in self.settings.concept_languages
        # and altlabels whithout language
        else:
            alt_labels = [label for label in labels if interesting_labels(label)]
            for label in alt_labels:
                self._add_label(concept, label, preferred)

    def _add_label(self, concept, label, preferred):
        concept.labels.append(
            DbLabel(
                value=str(label),
                language=label.language,
                preferred=preferred,
            )
        )
