from typing import AsyncGenerator

import aiohttp
from loguru import logger

from app.harvesters.exceptions.external_endpoint_failure import ExternalEndpointFailure
from app.harvesters.exceptions.unexpected_format_exception import (
    UnexpectedFormatException,
)


class HalApiClient:
    """Async client for HAL API"""

    HAL_API_URL = "https://api.archives-ouvertes.fr/search"

    async def fetch(self, query_string: str) -> AsyncGenerator[dict, None]:
        """
        Fetch the results from the HAL API

        :param query_string: the query string to send to the HAL API
        :return: A generator of results
        """
        try:
            async with aiohttp.ClientSession(
                connector=aiohttp.TCPConnector(limit=0)
            ) as session:
                async with session.get(f"{self.HAL_API_URL}/?{query_string}") as resp:
                    if resp.status == 200:
                        json_response = await resp.json()
                        # Hal API doesn't provide information about the error in the response body
                        if "error" in json_response.keys():
                            raise ExternalEndpointFailure(
                                f"Error response from HAL API for request : {query_string}"
                            )
                        if (
                            "response" not in json_response.keys()
                            or "docs" not in json_response["response"].keys()
                        ):
                            raise UnexpectedFormatException(
                                f"Unexpected format in HAL response: {json_response}"
                                f"for request : {query_string}"
                            )
                        for doc in json_response["response"]["docs"]:
                            # Raise unexpected format exception if the docid is missing
                            if doc.get("docid") is None:
                                logger.error(f"Missing docid in HAL response: {doc}")
                                continue
                            yield doc
                    else:
                        raise ExternalEndpointFailure(
                            f"Error code from HAL API for request : {query_string} "
                            f"with code {resp.status}"
                        )
        except aiohttp.ClientConnectorError as error:
            raise ExternalEndpointFailure(
                f"Cant connect to HAL API for request : {query_string} with error {error}"
            ) from error
