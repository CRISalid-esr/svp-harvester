# file: app/services/concepts/dummy_concept_solver.py

from rdflib import Literal

from app.db.models.concept import Concept as DbConcept
from app.services.concepts.concept_informations import ConceptInformations
from app.services.concepts.concept_solver import ConceptSolver
from app.services.errors.dereferencing_error import DereferencingError


class DummyConceptSolver(ConceptSolver):
    """
    Dummy concept solver that creates a concept from the given information
    without making any remote call.
    """

    def complete_information(self, concept_informations: ConceptInformations) -> None:
        if not concept_informations.uri:
            if concept_informations.code:
                concept_informations.uri = (
                    f"http://dummy.org/concept/{concept_informations.code}"
                )
            else:
                raise DereferencingError("Dummy solver needs at least a code or uri")

        if not concept_informations.code and concept_informations.uri:
            concept_informations.code = concept_informations.uri.split("/")[-1]

    async def solve(self, concept_informations: ConceptInformations) -> DbConcept:
        concept = DbConcept(uri=concept_informations.uri)

        # Add preferred label if available
        if concept_informations.label:
            self._add_labels(
                concept,
                labels=[
                    Literal(
                        concept_informations.label, lang=concept_informations.language
                    )
                ],
                preferred=True,
            )
        return concept
