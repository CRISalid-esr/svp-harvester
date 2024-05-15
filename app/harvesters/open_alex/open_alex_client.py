from typing import Generator

import aiohttp

from app.harvesters.exceptions.external_endpoint_failure import ExternalEndpointFailure
from app.harvesters.exceptions.unexpected_format_exception import (
    UnexpectedFormatException,
)


class OpenAlexClient:
    """Async client for OpenAlex API"""

    OPEN_ALEX_URL = "https://api.openalex.org/works"

    PER_PAGE = 25

    async def fetch(self, query_string: str) -> Generator[dict, None, None]:
        """
        Fetch the results from the OpenAlex API

        :param query_string: the query string to send to the OpenAlex API
        :return: A generator of results
        """
        page_number = 1
        while True:
            paginated_query = (
                f"{query_string}&page={page_number}&per_page={self.PER_PAGE}"
            )
            try:
                async with aiohttp.ClientSession(
                    connector=aiohttp.TCPConnector(limit=None)
                ) as session:
                    async with session.get(
                        f"{self.OPEN_ALEX_URL}?{paginated_query}"
                    ) as resp:
                        if resp.status == 200:
                            json_response = await resp.json()
                            if "results" not in json_response.keys():
                                raise UnexpectedFormatException(
                                    f"Unexpected format in OpenAlex response: {json_response} "
                                    f"for request : {query_string}"
                                )
                            if "error" in json_response.keys():
                                raise ExternalEndpointFailure(
                                    f"Error from OpenAlex API for request : {query_string} "
                                    f"with error {json_response['error']}"
                                )
                            for doc in json_response["results"]:
                                yield doc
                            meta = json_response.get("meta", {})
                            if (
                                meta.get("count", 0)
                                < meta.get("per_page", 0) * page_number
                            ):
                                break
                            page_number += 1
                        else:
                            raise ExternalEndpointFailure(
                                f"Error code from OpenAlex API for request : {query_string} "
                                f"with code {resp.status}"
                            )

            except aiohttp.ClientConnectorError as error:
                raise ExternalEndpointFailure(
                    f"Cant connect to OpenAlex API for request : {query_string} with error {error}"
                ) from error
