from typing import Generator

import aiohttp

from app.harvesters.exceptions.external_api_error import ExternalApiError


class HalApiClient:
    """Async client for HAL API"""

    HAL_API_URL = "https://api.archives-ouvertes.fr/search"

    async def fetch(self, query_string: str) -> Generator[dict, None, None]:
        """
        Fetch the results from the HAL API

        :param query_string: the query string to send to the HAL API
        :return: A generator of results
        """
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.HAL_API_URL}/?{query_string}") as resp:
                    if resp.status == 200:
                        json_response = await resp.json()
                        if "error" in json_response.keys():
                            raise ExternalApiError(
                                f"Error response from HAL API for request : {query_string}"
                            )
                        for doc in json_response["response"]["docs"]:
                            yield doc
                    else:
                        raise ExternalApiError(
                            f"Error code from HAL API for request : {query_string} "
                            f"with code {resp.status}"
                        )
        except aiohttp.ClientConnectorError as error:
            raise ExternalApiError(
                f"Cant connect to HAL API for request : {query_string} with error {error}"
            ) from error
