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

                pref_labels = concept_graph.objects(
                    rdflib.term.URIRef(idref_uri), SKOS.prefLabel
                )
                alt_labels = concept_graph.objects(
                    rdflib.term.URIRef(idref_uri), SKOS.altLabel
                )
                self._add_labels(
                    concept=concept, labels=list(pref_labels), preferred=True
                )
                self._add_labels(
                    concept=concept, labels=list(alt_labels), preferred=False
                )
                return concept

    def _add_labels(
        self,
        concept: DbConcept,
        labels: list[rdflib.term.Literal],
        preferred: bool = True,
    ):
        # If there is only one label, add it
        # If there are several labels, and one one them
        # is in self.settings.concept_languages or has no language,
        # add only labels whose language is in self.settings.concept_languages
        # and labels whithout language
        # If there are several labels, and none of them
        # is in self.settings.concept_languages or has no language,
        # add the first one in any language
        if len(labels) == 0:
            return
        if len(labels) == 1:
            self._add_label(concept, labels[0], preferred)
        else:
            labels_to_add = []
            for label in labels:
                if (
                    label.language is None
                    or label.language in self.settings.concept_languages
                ):
                    labels_to_add.append(label)
            if len(labels_to_add) == 0:
                labels_to_add.append(labels[0])
            for label in labels_to_add:
                self._add_label(concept, label, preferred)

    def _add_label(self, concept, label, preferred):
        concept.labels.append(
            DbLabel(
                value=str(label),
                language=label.language,
                preferred=preferred,
            )
        )

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
