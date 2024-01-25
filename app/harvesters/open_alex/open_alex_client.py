from typing import Generator

import aiohttp
from loguru import logger

from app.harvesters.exceptions.external_endpoint_failure import ExternalEndpointFailure
from app.harvesters.exceptions.unexpected_format_exception import (
    UnexpectedFormatException,
)


class OpenAlexClient:
    """Async client for OpenAlex API"""

    OPEN_ALEX_URL = "https://api.openalex.org/works"

    async def fetch(self, query_string: str) -> Generator[dict, None, None]:
        """
        Fetch the results from the OpenAlex API

        :param query_string: the query string to send to the OpenAlex API
        :return: A generator of results
        """

        try:
            async with aiohttp.ClientSession(
                connector=aiohttp.TCPConnector(limit=None)
            ) as session:
                async with session.get(f"{self.OPEN_ALEX_URL}?{query_string}") as resp:
                    logger.debug(
                        f"Fetching OpenAlex results for query {self.OPEN_ALEX_URL}?{query_string}"
                    )
                    if resp.status == 200:
                        json_response = await resp.json()
                        if "results" not in json_response.keys():
                            raise UnexpectedFormatException(
                                f"Unexpected format in OpenAlex response: {json_response} "
                                f"for request : {query_string}"
                            )
                        for doc in json_response["results"]:
                            yield doc
                    else:
                        raise ExternalEndpointFailure(
                            f"Error code from OpenAlex API for request : {query_string} "
                            f"with code {resp.status}"
                        )

        except aiohttp.ClientConnectorError as error:
            raise ExternalEndpointFailure(
                f"Cant connect to OpenAlex API for request : {query_string} with error {error}"
            ) from error
