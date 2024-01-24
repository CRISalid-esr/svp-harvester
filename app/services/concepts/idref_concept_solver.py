import re

import aiohttp
import rdflib
from rdflib import Graph, SKOS

from app.db.models.concept import Concept as DbConcept
from app.db.models.label import Label as DbLabel
from app.services.concepts.concept_solver import ConceptSolver


class IdRefConceptSolver(ConceptSolver):
    """
    IdRef concept solver
    """

    async def solve(self, concept_id: str) -> DbConcept:
        """
        Solves an IdRef concept from a concept id
        :param concept_id: concept id (numeric or uri)
        :return: Concept
        """
        idref_url, idref_uri = await self._build_url_from_concept_id_or_uri(concept_id)
        async with aiohttp.ClientSession() as session:
            async with session.get(idref_url) as response:
                # TODO handle error response
                xml = await response.text()
                # TODO handle format exception
                concept_graph = Graph().parse(data=xml, format="xml")
                concept = DbConcept(uri=idref_uri)

                for pref_label in concept_graph.objects(
                    rdflib.term.URIRef(idref_uri), SKOS.prefLabel
                ):
                    concept.labels.append(
                        DbLabel(
                            value=str(pref_label),
                            language=pref_label.language,
                            preferred=True,
                        )
                    )
                return concept

    async def _build_url_from_concept_id_or_uri(self, concept_id):
        original_concept_id = concept_id
        match = re.search(r"https?://www.idref.fr/(\d+)/id", concept_id)
        if match is not None:
            concept_id = match.group(1)
        if not concept_id.isnumeric():
            raise ValueError(f"Invalid idref concept id or uri {original_concept_id}")
        idref_url = f"https://www.idref.fr/{concept_id}.rdf"
        idref_uri = f"http://www.idref.fr/{concept_id}/id"
        return idref_url, idref_uri
