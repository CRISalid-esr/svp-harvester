from enum import Enum

from app.db.models.concept import Concept as DbConcept
from app.services.concepts.concept_solver import ConceptSolver
from app.services.concepts.idref_concept_solver import IdRefConceptSolver
from app.services.concepts.unknown_authority_exception import UnknownAuthorityException
from app.services.concepts.wikidata_concept_solver import WikidataConceptSolver


class ConceptFactory:
    """
    Concept factory : solves a concept from a concept id and an optional source
    by calling the appropriate solver
    """

    class ConceptSources(Enum):
        """
        Closed list of supported sources
        """

        IDREF = "IDREF"
        WIKIDATA = "WIKIDATA"
        # add more sources here

    @staticmethod
    async def solve(
        concept_id: str, concept_source: ConceptSources = None
    ) -> DbConcept:
        """
        Solves a concept from a concept id and an optional source
        :param concept_id: id or uri of the concept
        :param concept_source: source of the concept, among supported sources
        :return:
        """
        if concept_source is None:
            # infer source from uri
            concept_source = ConceptFactory._infer_source(concept_id)
        # create a solver adapted to the source
        solver: ConceptSolver = ConceptFactory._create_solver(concept_source)
        # solve the concept
        return await solver.solve(concept_id)

    @classmethod
    def _create_solver(cls, concept_source) -> ConceptSolver:
        if concept_source == ConceptFactory.ConceptSources.IDREF:
            return IdRefConceptSolver()
        if concept_source == ConceptFactory.ConceptSources.WIKIDATA:
            return WikidataConceptSolver()
        # add more sources here
        # if no solver is found, raise an exception
        raise ValueError(f"Unknown concept source {concept_source}")

    @classmethod
    def _infer_source(cls, concept_id) -> ConceptSources:
        # for id "http://www.idref.fr/027219372/id", return ConceptSources.IDREF
        # for id "http://www.wikidata.org/entity/Q1234", return ConceptSources.WIKIDATA
        # add more sources here
        if concept_id.startswith("http://www.idref.fr"):
            return ConceptFactory.ConceptSources.IDREF  # idref
        if concept_id.startswith("http://www.wikidata.org"):
            return ConceptFactory.ConceptSources.WIKIDATA
        # add more sources here
        # if no source is found, raise an exception
        raise UnknownAuthorityException(concept_id)