from typing import AsyncGenerator

import aiohttp
from aiosparql.client import SPARQLClient
from app.harvesters.exceptions.external_endpoint_failure import ExternalEndpointFailure

from app.harvesters.idref.idref_sparql_client import DATA_IDREF_FR_URL


class OpenEditionSparqlClient:
    """
    Async client for data.idref.fr SPARQL API, wrapper around aiosparql
    """

    async def fetch_uri_publications(self, query: str) -> AsyncGenerator[dict, None]:
        """
        Fetch the uri publications from Open Edition for a
        given author from the Idref sparql endpoint
        """
        client: SPARQLClient = self._get_client()
        try:
            response = await client.query(query)
            for result in response.get("results", {}).get("bindings", []):
                yield {
                    "uri": result.get("uri", {}).get("value"),
                    "citation": result.get("citation", {}),
                    "datePub": result.get("datePub", {}),
                    "secondary_source": "OPEN_EDITION",
                }
        except Exception as error:
            raise ExternalEndpointFailure(
                f"Failed to fetch uris from data.idref.fr: {error}"
            ) from error
        finally:
            await client.close()

    def _get_client(self) -> SPARQLClient:
        return SPARQLClient(
            DATA_IDREF_FR_URL, connector=aiohttp.TCPConnector(limit=None)
        )
