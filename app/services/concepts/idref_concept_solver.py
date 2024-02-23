import re
from typing import Tuple

from app.services.concepts.rdf_concept_solver import RdfConceptSolver


class IdRefConceptSolver(RdfConceptSolver):
    """
    IdRef concept solver
    """

    def get_uri(self, concept_id: str) -> str:
        idref_uri, _ = self._build_uri_and_url(concept_id)
        return idref_uri

    def _build_uri_and_url(self, concept_id_or_uri: str) -> Tuple[str, str]:
        original_concept_id = concept_id_or_uri
        match = re.search(r"https?://www.idref.fr/(\d+X?)/id", concept_id_or_uri)
        if match is not None:
            concept_id_or_uri = match.group(1)
        if not concept_id_or_uri[0:-1].isdigit():
            raise ValueError(f"Invalid idref concept id or uri {original_concept_id}")
        idref_url = f"https://www.idref.fr/{concept_id_or_uri}.rdf"
        idref_uri = f"http://www.idref.fr/{concept_id_or_uri}/id"
        return idref_uri, idref_url
