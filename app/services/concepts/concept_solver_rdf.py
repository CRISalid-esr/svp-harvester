from typing import List, Tuple

from rdflib import SKOS, Graph, term

from app.services.concepts.concept_solver import ConceptSolver


class ConceptSolverRdf(ConceptSolver):
    """
    Abstract mother class for concept solvers using RDF
    """

    async def solve(self, concept_id: str):
        raise NotImplementedError

    def _get_labels(self, concept_data: Graph, uri: str) -> List[Tuple[str, bool]]:
        """
        Get labels from a concept graph
        :param concept_graph: concept graph
        :param uri: concept uri

        :return: labels
        """
        pref_labels = concept_data.objects(term.URIRef(uri), SKOS.prefLabel)
        alt_labels = concept_data.objects(term.URIRef(uri), SKOS.altLabel)
        return [(pref_labels, True), (alt_labels, False)]
