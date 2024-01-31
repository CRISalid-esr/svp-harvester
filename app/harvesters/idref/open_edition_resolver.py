from urllib.parse import urlparse
import xml.etree.ElementTree as ET
import aiohttp

from app.harvesters.exceptions.external_endpoint_failure import ExternalEndpointFailure


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
        self.connector = aiohttp.TCPConnector(limit=0)

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
        try:
            async with aiohttp.ClientSession(
                connector=aiohttp.TCPConnector(limit=0)
            ) as session:
                async with session.get(document_url) as resp:
                    if resp.status == 200:
                        response_text = await resp.text()
                        root = ET.fromstring(response_text.strip())
                        return root
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
