from typing import Generator

from app.harvesters.exceptions.external_endpoint_failure import (
    ExternalEndpointFailure,
    handle_external_endpoint_failure,
)
from app.harvesters.exceptions.unexpected_format_exception import (
    UnexpectedFormatException,
)
from app.http.aio_http_client_manager import AioHttpClientManager


class OpenAlexClient:
    """Async client for OpenAlex API"""

    OPEN_ALEX_URL = "https://api.openalex.org/works"

    PER_PAGE = 25

    @handle_external_endpoint_failure("OpenAlex")
    async def fetch(self, url: str) -> Generator[dict, None, None]:
        """
        Fetch the results from the OpenAlex API

        :param url: the query string to send to the OpenAlex API
        :return: A generator of results
        """
        page_number = 1
        session = await AioHttpClientManager.get_session()
        while True:
            paginated_query = f"{url}&page={page_number}&per_page={self.PER_PAGE}"
            async with session.get(f"{self.OPEN_ALEX_URL}?{paginated_query}") as resp:
                if resp.status == 200:
                    json_response = await resp.json()
                    if "results" not in json_response.keys():
                        raise UnexpectedFormatException(
                            f"Unexpected format in OpenAlex response: {json_response} "
                            f"for request : {url}"
                        )
                    if "error" in json_response.keys():
                        raise ExternalEndpointFailure(
                            f"Error from OpenAlex API for request : {url} "
                            f"with error {json_response['error']}"
                        )
                    for doc in json_response["results"]:
                        yield doc
                    meta = json_response.get("meta", {})
                    if meta.get("count", 0) < meta.get("per_page", 0) * page_number:
                        break
                    page_number += 1
                else:
                    await resp.release()
                    raise ExternalEndpointFailure(
                        f"Error code from OpenAlex API for request : {url} "
                        f"with code {resp.status}"
                    )
