from typing import Generator
import xml.etree.ElementTree as ET
import aiohttp
from loguru import logger


from app.config import get_app_settings
from app.harvesters.exceptions.external_endpoint_failure import ExternalEndpointFailure


class ScopusClient:
    """
    Async client for Scopus API
    """

    SCOPUS_URL = "https://api.elsevier.com/content/search/scopus"

    NAMESPACE = {
        "default": "http://www.w3.org/2005/Atom",
        "dc": "http://purl.org/dc/elements/1.1/",
        "opensearch": "http://a9.com/-/spec/opensearch/1.1/",
        "prism": "http://prismstandard.org/namespaces/basic/2.0/",
        "atom": "http://www.w3.org/2005/Atom",
    }

    def __init__(self) -> None:
        self.settings = get_app_settings()

    async def fetch(self, query_string: str) -> Generator[dict, None, None]:
        """
        Fetch the results from Scopus API
        """

        try:
            async with aiohttp.ClientSession(
                connector=aiohttp.TCPConnector(limit=None),
                headers={"Accept": "application/xml"},
            ) as session:
                async with session.get(
                    f"{self.SCOPUS_URL}?{query_string}&apiKey={self.settings.scopus_api_key}",
                ) as resp:
                    if resp.status == 200:
                        xml = await resp.text()
                        root = ET.fromstring(xml)
                        count = root.find(
                            "opensearch:totalResults", self.NAMESPACE
                        ).text
                        if int(count) == 0:
                            yield
                        else:
                            for doc in root.findall(".//default:entry", self.NAMESPACE):
                                yield doc
                    else:
                        raise ExternalEndpointFailure(
                            f"Error code from Scopus API for request: {query_string} "
                            f"With code {resp.status}"
                        )

        except aiohttp.ClientConnectionError as error:
            raise ExternalEndpointFailure(
                f"Cant connect to Scopus API for request: {query_string} with error {error}"
            ) from error
