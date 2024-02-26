from abc import ABC

from app.services.concepts.concept_informations import ConceptInformations
from app.services.concepts.concept_solver import ConceptSolver
from app.services.concepts.dereferencing_error import DereferencingError


class JelConceptSolver(ConceptSolver, ABC):
    """
    JEL concept solver
    """

    def complete_information(self, concept_informations: ConceptInformations) -> None:
        """
        Concept code from hal is a concatenation of type : G1.G12.G123
        Concatenate the JEL namespace with the last part of the concept id
        """
        if concept_informations.uri is None and concept_informations.code is not None:
            concept_code = concept_informations.code.rsplit(".", 1)[-1]
            concept_informations.uri = (
                f"http://zbw.eu/beta/external_identifiers/jel#{concept_code}"
            )
        elif concept_informations.uri is not None and concept_informations.code is None:
            concept_code = concept_informations.uri.split("#")[-1]
            concept_informations.code = concept_code
        else:
            raise DereferencingError(
                "Unable to build required fields to solve JEL concept"
                f"from information : {concept_informations}"
            )
