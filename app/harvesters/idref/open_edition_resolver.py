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

    BASE_URL_REVUE = (
        "http://oai.openedition.org/?verb=GetRecord"
        "&identifier=oai:revues.org:{}/{}"
        "&metadataPrefix=qdc"
    )
    BASE_URL_CHAPTER = (
        "http://oai.openedition.org/?verb=GetRecord"
        "&identifier=oai:books.openedition.org:{}/{}"
        "&metadataPrefix=qdc"
    )

    def __init__(self):
        self.http_client = ResolverHTTPClient()

    def _parse_uri(self, uri: str) -> tuple[str, str, str]:
        """
        Parse the uri from open edition to get the records, the identifier and the type reference
        """
        parsed_uri = urlparse(uri)
        type_reference = parsed_uri.netloc.split(".")[0]
        path_parts = parsed_uri.path.split("/")
        records = path_parts[1]
        identifier = path_parts[2]
        return records, identifier, type_reference

    def _create_uri(self, records: str, identifier: str, type_reference) -> str:
        """
        Create the uri to fetch the record from OAI Open Edition
        """
        if type_reference == "journals":
            return self.BASE_URL_REVUE.format(records, identifier)
        if type_reference == "books":
            return self.BASE_URL_CHAPTER.format(records, identifier)
        raise AssertionError(
            f"Unknown type reference: {type_reference} for {records} {identifier}"
        )

    async def fetch(self, document_uri: str) -> ET.Element:
        """
        Get the record XML from OAI Open Edition
        """
        records, identifier, type_reference = self._parse_uri(document_uri)
        document_url = self._create_uri(records, identifier, type_reference)
        response_text = await self.http_client.get(document_url)
        try:
            root = ET.fromstring(response_text.strip())
        except ET.ParseError as error:
            raise UnexpectedFormatException(
                f"Error while parsing the XML from {document_url} : {response_text}"
            ) from error
        return root
