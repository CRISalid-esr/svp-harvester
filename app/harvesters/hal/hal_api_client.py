from typing import AsyncGenerator

from aiohttp import ClientTimeout
from loguru import logger

from app.harvesters.exceptions.external_endpoint_failure import (
    ExternalEndpointFailure,
    handle_external_endpoint_failure,
)
from app.harvesters.exceptions.unexpected_format_exception import (
    UnexpectedFormatException,
)
from app.http.aio_http_client_manager import AioHttpClientManager


class HalApiClient:
    """Async client for HAL API"""

    HAL_API_URL = "https://api.archives-ouvertes.fr/search"

    def __init__(self, timeout: int = 60):
        """
        Initialize the HAL API client.

        :param timeout: The timeout for requests to the HAL API in seconds.
        """
        self.timeout = timeout

    @handle_external_endpoint_failure("HAL")
    async def fetch(self, url: str) -> AsyncGenerator[dict, None]:
        """
        Fetch the results from the HAL API

        :param url: the query string to send to the HAL API
        :return: A generator of results
        """
        session = await AioHttpClientManager.get_session()
        request_timeout = (
            ClientTimeout(
                total=self.timeout,  # overall cap on the request lifecycle
                connect=10,  # max time to establish TCP connection
                sock_read=30,  # max time to wait for server response data
                sock_connect=10,  # max time to establish socket (useful behind proxies)
            ),
        )
        logger.info(f"Fetching HAL API with query: {self.HAL_API_URL}/?{url}")
        async with session.get(
            f"{self.HAL_API_URL}/?{url}", timeout=request_timeout
        ) as resp:
            if resp.status == 200:
                json_response = await resp.json()
                # Hal API doesn't provide information about the error in the response body
                if "error" in json_response.keys():
                    raise ExternalEndpointFailure(
                        f"Error response from HAL API for request : {url}"
                    )
                if (
                    "response" not in json_response.keys()
                    or "docs" not in json_response["response"].keys()
                ):
                    raise UnexpectedFormatException(
                        f"Unexpected format in HAL response: {json_response}"
                        f"for request : {url}"
                    )
                for doc in json_response["response"]["docs"]:
                    if doc.get("halId_s") is None:
                        logger.error(f"Missing halId_s in HAL response: {doc}")
                        continue
                    yield doc
            else:
                await resp.release()
                raise ExternalEndpointFailure(
                    f"Error code from HAL API for request : {url} "
                    f"with code {resp.status}"
                )
