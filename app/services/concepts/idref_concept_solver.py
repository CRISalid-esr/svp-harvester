import re

import aiohttp
import rdflib
from aiohttp import ClientTimeout
from rdflib import Graph

from app.db.models.concept import Concept as DbConcept
from app.services.concepts.concept_solver_rdf import ConceptSolverRdf
from app.services.concepts.dereferencing_error import DereferencingError


class IdRefConceptSolver(ConceptSolverRdf):
    """
    IdRef concept solver
    """

    def get_uri(self, concept_id: str) -> str:
        _, idref_uri = self._build_url_from_concept_id_or_uri(concept_id)
        return idref_uri

    async def solve(self, concept_id: str) -> DbConcept:
        """
        Solves an IdRef concept from a concept id
        :param concept_id: concept id (numeric or uri)
        :return: Concept
        """
        idref_url, idref_uri = self._build_url_from_concept_id_or_uri(concept_id)
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

                    [  # pylint: disable=expression-not-assigned
                        self._add_labels(
                            concept=concept, labels=list(label[0]), preferred=label[1]
                        )
                        for label in self._get_labels(concept_graph, idref_uri)
                    ]

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

    def _build_url_from_concept_id_or_uri(self, concept_id):
        original_concept_id = concept_id
        match = re.search(r"https?://www.idref.fr/(\d+X?)/id", concept_id)
        if match is not None:
            concept_id = match.group(1)
        if not concept_id[0:-1].isdigit():
            raise ValueError(f"Invalid idref concept id or uri {original_concept_id}")
        idref_url = f"https://www.idref.fr/{concept_id}.rdf"
        idref_uri = f"http://www.idref.fr/{concept_id}/id"
        return idref_url, idref_uri
