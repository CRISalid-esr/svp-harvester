import aiohttp
from rdflib import Graph

from app.harvesters.exceptions.external_endpoint_failure import ExternalEndpointFailure


class RdfResolver:
    """Async client for HAL API"""

    def __init__(self):
        self.connector = aiohttp.TCPConnector(limit=0)

    async def fetch(self, document_uri: str, output_format: str = "xml") -> Graph:
        """
        Fetch the results from the HAL API

        :param document_uri: the document URI for which to fetch the RDF
        :return: A generator of results
        """
        try:
            async with aiohttp.ClientSession(
                connector=aiohttp.TCPConnector(limit=0)
            ) as session:
                async with session.get(document_uri) as resp:
                    if resp.status == 200:
                        response_text = await resp.text()
                        graph = Graph().parse(data=response_text, format=output_format)
                        return graph
                    raise ExternalEndpointFailure(
                        f"Error code while resolving URI : {document_uri} "
                        f"with code {resp.status}"
                    )
        except aiohttp.ClientConnectorError as error:
            raise ExternalEndpointFailure(
                f"Cant resolve URI : {document_uri} with error {error}"
            ) from error
        except Exception as error:
            raise ExternalEndpointFailure(
                f"Error while resolving URI : {document_uri} with error {error}"
            ) from error
