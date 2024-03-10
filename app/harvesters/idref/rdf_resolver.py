from xml.sax import SAXParseException

from rdflib import Graph
from rdflib.exceptions import ParserError

from app.harvesters.exceptions.unexpected_format_exception import (
    UnexpectedFormatException,
)
from app.harvesters.idref.resolver_http_client import ResolverHTTPClient

DEFAULT_RDF_TIMEOUT = 30


class RdfResolver:
    """
    Async RDF Resolver for various RDF sources
    """

    def __init__(self, timeout: int = DEFAULT_RDF_TIMEOUT):
        self.http_client = ResolverHTTPClient(timeout=timeout)

    async def fetch(self, document_uri: str, output_format: str = "xml") -> Graph:
        """
        Fetch the results from the HAL API

        :param document_uri: the document URI for which to fetch the RDF
        :return: A generator of results
        """
        response_text = await self.http_client.get(document_uri)
        try:
            graph = Graph().parse(data=response_text, format=output_format)
            return graph
        except (ParserError, SAXParseException) as error:
            raise UnexpectedFormatException(
                f"Error while parsing the RDF from {document_uri} : {response_text}"
            ) from error
