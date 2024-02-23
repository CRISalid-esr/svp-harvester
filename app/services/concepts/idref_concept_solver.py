import re
from typing import Tuple

from app.services.concepts.concept_informations import ConceptInformations
from app.services.concepts.rdf_concept_solver import RdfConceptSolver


class IdRefConceptSolver(RdfConceptSolver):
    """
    IdRef concept solver
    """

    def add_uri(self, concept_information: ConceptInformations) -> str:
        original_concept_uri = concept_information.uri
        match = re.search(r"https?://www.idref.fr/(\d+X?)/id", concept_information.uri)
        if match is not None:
            concept_code = match.group(1)
        if not concept_code[0:-1].isdigit():
            raise ValueError(f"Invalid idref concept id or uri {original_concept_uri}")
        concept_information.url = f"https://www.idref.fr/{concept_code}.rdf"
        concept_information.uri = f"http://www.idref.fr/{concept_code}/id"
