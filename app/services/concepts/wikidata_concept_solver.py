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
        raise DereferencingError("Wikidata concept solver not implemented")
