import re

import aiohttp
import rdflib
from aiohttp import ClientTimeout
from rdflib import Graph, SKOS

from app.db.models.concept import Concept as DbConcept
from app.db.models.label import Label as DbLabel
from app.services.concepts.concept_solver import ConceptSolver
from app.services.concepts.dereferencing_error import DereferencingError


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
        try:
            async with aiohttp.ClientSession(
                timeout=ClientTimeout(total=float(2))
            ) as session:
                async with session.get(idref_url) as response:
                    if not 200 <= response.status < 300:
                        raise DereferencingError(
                            f"Endpoint returned status {response.status}"
                            f" while dereferencing {idref_url}"
                        )
                    xml = await response.text()
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
        except aiohttp.ClientError as error:
            raise DereferencingError(
                f"Endpoint failure while dereferencing {idref_url} with message {error}"
            ) from error
        except rdflib.exceptions.ParserError as error:
            raise DereferencingError(
                f"Error while parsing xml from {idref_url} with message {error}"
            ) from error
        except Exception as error:
            raise DereferencingError(
                f"Unknown error while dereferencing {idref_url} with message {error}"
            ) from error

    def _add_labels(
        self,
        concept: DbConcept,
        labels: list[rdflib.term.Literal],
        preferred: bool = True,
    ):
        def interesting_labels(label):
            return (
                label.language in self.settings.concept_languages
                or label.language is None
            )

        if len(labels) == 0:
            return
        # If there is only one preflabel, add it
        # If there are several preflabels, and one one them
        # is in self.settings.concept_languages or has no language,
        # add only preflabels whose language is in self.settings.concept_languages
        # and preflabels whithout language
        # If there are several preflabels, and none of them
        # is in self.settings.concept_languages or has no language,
        # add the first one in any language
        if preferred:
            preferred_labels = [label for label in labels if interesting_labels(label)]
            for label in preferred_labels or [labels[0]]:
                self._add_label(concept, label, preferred)
        # Add all altlabels whose language is in self.settings.concept_languages
        # and altlabels whithout language
        else:
            alt_labels = [label for label in labels if interesting_labels(label)]
            for label in alt_labels:
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
        match = re.search(r"https?://www.idref.fr/(\d+X?)/id", concept_id)
        if match is not None:
            concept_id = match.group(1)
        if not concept_id[0:-1].isdigit():
            raise ValueError(f"Invalid idref concept id or uri {original_concept_id}")
        idref_url = f"https://www.idref.fr/{concept_id}.rdf"
        idref_uri = f"http://www.idref.fr/{concept_id}/id"
        return idref_url, idref_uri
