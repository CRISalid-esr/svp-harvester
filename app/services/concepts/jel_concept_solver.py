from abc import ABC

from app.services.concepts.concept_solver import ConceptSolver


class JelConceptSolver(ConceptSolver, ABC):
    """
    JEL concept solver
    """

    def add_uri(self, concept_id: str) -> str:
        """
        Concatenate the JEL namespace with the last part of the concept id
        """
        concept_code = concept_id.rsplit(".", 1)[-1]
        return f"http://zbw.eu/beta/external_identifiers/jel#{concept_code}"
