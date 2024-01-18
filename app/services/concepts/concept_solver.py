from abc import ABC, abstractmethod

from app.db.models.concept import Concept as DbConcept


class ConceptSolver(ABC):
    """
    Abstract mother class for concept solvers
    """

    @abstractmethod
    async def solve(self, concept_id: str) -> DbConcept:
        """
        Solves a concept from a concept id
        :param concept_id: concept id
        :return: Concept
        """
