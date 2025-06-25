from aiohttp import ClientTimeout

from app.harvesters.exceptions.external_endpoint_failure import (
    ExternalEndpointFailure,
    handle_external_endpoint_failure,
)
from app.http_client import get_aiohttp_session


class ResolverHTTPClient:
    """
    Generic HTTP client for resolving URIs
    """

    def __init__(self, timeout: int = 30):
        self.timeout = timeout

    @handle_external_endpoint_failure("external resolver")
    async def get(self, url: str) -> str:
        """
        Get any document from remote URL as text

        :param url: the URL to fetch
        :return: the document as text
        """
        session = get_aiohttp_session()
        request_timeout = ClientTimeout(total=float(self.timeout))
        async with session.get(url, timeout=request_timeout) as resp:
            if resp.status == 200:
                return await resp.text()
            await resp.release()
            raise ExternalEndpointFailure(
                f"Error code while resolving URI : {url} with code {resp.status}"
            )
