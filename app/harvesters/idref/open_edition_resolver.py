import xml.etree.ElementTree as ET
from urllib.parse import urlparse

from app.harvesters.exceptions.unexpected_format_exception import (
    UnexpectedFormatException,
)
from app.harvesters.idref.resolver_http_client import ResolverHTTPClient


class OpenEditionResolver:
    """
    Async client for Open Edition API
    """

    BASE_URL = (
        "http://oai.openedition.org/?verb=GetRecord"
        "&identifier=oai:revues.org:{}/{}"
        "&metadataPrefix=qdc"
    )

    def __init__(self):
        self.http_client = ResolverHTTPClient()

    def parse_uri(self, uri: str) -> (str, str):
        """
        Parse the uri from open edition to get the records and the identifier
        """
        parsed_uri = urlparse(uri)
        path_parts = parsed_uri.path.split("/")
        records = path_parts[1]
        identifier = path_parts[2]
        return records, identifier

    def create_uri(self, records: str, identifier: str) -> str:
        """
        Create the uri to fetch the record from OAI Open Edition
        """
        return self.BASE_URL.format(records, identifier)

    async def fetch(self, document_uri: str) -> ET.Element:
        """
        Get the record XML from OAI Open Edition
        """
        records, identifier = self.parse_uri(document_uri)
        document_url = self.create_uri(records, identifier)
        response_text = await self.http_client.get(document_url)
        try:
            root = ET.fromstring(response_text.strip())
        except ET.ParseError as error:
            raise UnexpectedFormatException(
                f"Error while parsing the XML from {document_url} : {response_text}"
            ) from error
        return root
