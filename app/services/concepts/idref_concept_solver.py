import re

from app.services.concepts.rdf_concept_solver import RdfConceptSolver


class IdRefConceptSolver(RdfConceptSolver):
    """
    IdRef concept solver
    """

    def get_uri(self, concept_id: str) -> str:
        _, idref_uri = self._build_url_from_concept_id_or_uri(concept_id)
        return idref_uri

    def _build_url_from_concept_id_or_uri(self, concept_id):
        original_concept_id = concept_id
        match = re.search(r"https?://www.idref.fr/(\d+X?)/id", concept_id)
        if match is not None:
            concept_id = match.group(1)
        if not concept_id[0:-1].isdigit():
            raise ValueError(f"Invalid idref concept id or uri {original_concept_id}")
        idref_url = f"https://www.idref.fr/{concept_id}.rdf"
        idref_uri = f"http://www.idref.fr/{concept_id}/id"
        return idref_uri, idref_url
