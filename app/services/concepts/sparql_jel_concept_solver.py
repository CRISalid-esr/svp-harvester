import aiohttp
from aiohttp import ClientError
from aiosparql.client import SPARQLClient
from rdflib import Literal

from app.config import get_app_settings
from app.db.models.concept import Concept as DbConcept
from app.services.concepts.concept_informations import ConceptInformations
from app.services.concepts.dereferencing_error import DereferencingError
from app.services.concepts.jel_concept_solver import JelConceptSolver


class SparqlJelConceptSolver(JelConceptSolver):
    """
    JEL concept solver
    """

    QUERY_TEMPLATE = """
    PREFIX skos: <http://www.w3.org/2004/02/skos/core#>

    SELECT ?prefLabel ?altLabel
    WHERE {
      <URI> skos:prefLabel ?prefLabel .
      OPTIONAL {
        <URI> skos:altLabel ?altLabel .
      }
    }
    """

    def _get_client(self) -> SPARQLClient:
        settings = get_app_settings()
        assert (
            settings.svp_jel_proxy_url is not None
        ), "SVP_JEL_PROXY_URL environment variable must be set"
        return SPARQLClient(
            settings.svp_jel_proxy_url,
            connector=aiohttp.TCPConnector(limit=0),
            timeout=aiohttp.ClientTimeout(total=float(self.timeout)),
        )

    async def solve(self, concept_informations: ConceptInformations) -> DbConcept:
        """
        Solves a JEL concept from a concept id
        from a Fuseki endpoint

        :param concept_id: JEL code
        :return: Concept
        """
        query = self.QUERY_TEMPLATE.replace("URI", concept_informations.uri)
        client: SPARQLClient = self._get_client()
        try:
            sparql_response = await client.query(query)
            concept = DbConcept(uri=concept_informations.uri)
            labels = sparql_response["results"]["bindings"]
            pref_labels = [
                label["prefLabel"]["value"] for label in labels if "prefLabel" in label
            ]
            if not pref_labels:
                raise DereferencingError(
                    "JEL Sparql endpoint returned no prefLabel "
                    f"while dereferencing {concept_informations.uri}"
                )
            self._add_labels(
                concept,
                list(
                    {
                        Literal(
                            label["prefLabel"]["value"],
                            lang=label["prefLabel"]["xml:lang"],
                        )
                        for label in labels
                        if "prefLabel" in label
                    }
                ),
                True,
            )
            self._add_labels(
                concept,
                list(
                    {
                        Literal(
                            label["altLabel"]["value"],
                            lang=label["altLabel"]["xml:lang"],
                        )
                        for label in labels
                        if "altLabel" in label
                    }
                ),
                False,
            )
            return concept
        except ClientError as error:
            raise DereferencingError(
                "Endpoint failure while querying Fuseki sparql endpoint "
                f"{get_app_settings().svp_jel_proxy_url} "
                f"for concept_id {concept_informations.uri} with message {error}"
            ) from error
        except Exception as error:
            raise DereferencingError(
                "Unknown error while querying Fuseki sparql endpoint "
                f"{get_app_settings().svp_jel_proxy_url} "
                f"for concept_id {concept_informations.uri} with message {error}"
            ) from error
        finally:
            await client.close()
