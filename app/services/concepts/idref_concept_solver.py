from app.services.concepts.concept_solver import ConceptSolver
from app.db.models.concept import Concept as DbConcept


class IdRefConceptSolver(ConceptSolver):
    """
    IdRef concept solver
    """

    async def solve(self, concept_id: str) -> DbConcept:
        """
        Solves an IdRef concept from a concept id
        :param concept_id: concept id
        :return: Concept
        """
