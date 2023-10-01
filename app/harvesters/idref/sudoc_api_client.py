import re

import aiohttp
from rdflib import Graph

from app.harvesters.exceptions.external_endpoint_failure import ExternalEndpointFailure


class SudocApiClient:
    """Async client for HAL API"""

    API_URL_SUFFIX = "http://www.sudoc.fr/"

    def __init__(self):
        self.connector = aiohttp.TCPConnector(limit=None)

    async def fetch(self, document_id: str) -> Graph:
        """
        Fetch the results from the HAL API

        :param document_id: the document URI for which to fetch the RDF
        :return: A generator of results
        """
        assert document_id.startswith(self.API_URL_SUFFIX), "Invalid Sudoc Id"
        assert document_id.endswith("/id"), "Provided Sudoc URI should end with /id"
        # with regular expression, replace trailing "/id" by '.rdf' in document_uri
        document_uri = re.sub(r"/id$", ".rdf", document_id)
        # with regular expression, replace "http://" by "https://" in document_uri
        document_uri = re.sub(r"^http://", "https://", document_uri)
        try:
            async with aiohttp.ClientSession(
                connector=aiohttp.TCPConnector(limit=None)
            ) as session:
                async with session.get(document_uri) as resp:
                    if resp.status == 200:
                        response_text = await resp.text()
                        graph = Graph().parse(data=response_text, format="xml")
                        return graph
                    raise ExternalEndpointFailure(
                        f"Error code from Sudoc API for URI : {document_uri} "
                        f"with code {resp.status}"
                    )
        except aiohttp.ClientConnectorError as error:
            raise ExternalEndpointFailure(
                f"Cant connect to Sudoc API for URI : {document_uri} with error {error}"
            ) from error
        except Exception as error:
            raise ExternalEndpointFailure(
                f"Error while fetching Sudoc API for URI : {document_uri} with error {error}"
            ) from error
