import re
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
        if response_text:
            clean_response_text = self._clean_response_text(response_text)

            try:
                graph = Graph().parse(data=clean_response_text, format=output_format)
                return graph
            except (ParserError, SAXParseException) as error:
                raise UnexpectedFormatException(
                    f"Error while parsing the RDF from {document_uri} : {clean_response_text}"
                ) from error
        raise UnexpectedFormatException(
            f"Empty response from {document_uri} : {response_text}"
        )

    def _clean_response_text(self, response_text: str) -> str:
        """
        Clean the response text by removing empty date fields or fixing invalid date formats

        :param response_text: The raw XML response text
        :return: Clean XML response text
        """
        # List of regular expressions to match different empty date field patterns
        empty_patterns = [
            re.compile(r"<dc:date[^>]*></dc:date>"),
            re.compile(r"<dcterms:date[^>]*?/>"),
        ]
        for pattern in empty_patterns:
            response_text = pattern.sub("", response_text)

        # Fix invalid Persée datetimes like 2024-09-07BST21:13:02
        # -> 2024-09-07T21:13:02+01:00
        response_text = re.sub(
            r"(>)(\d{4}-\d{2}-\d{2})BST(\d{2}:\d{2}:\d{2})(<)",
            r"\1\2T\3+01:00\4",
            response_text,
        )

        return response_text
