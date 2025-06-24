from typing import Optional

import aiohttp

from app.config import get_app_settings

_connector: Optional[aiohttp.TCPConnector] = None
_session: Optional[aiohttp.ClientSession] = None


def get_aiohttp_connector() -> aiohttp.TCPConnector:
    """
    Get the aiohttp TCP connector with configured limits and DNS cache TTL.
    :return: aiohttp.TCPConnector instance
    """
    global _connector  # pylint: disable=global-statement
    if _connector is None:
        settings = get_app_settings()
        _connector = aiohttp.TCPConnector(
            limit=settings.http_client_limit,
            ttl_dns_cache=settings.http_client_ttl_dns_cache,
        )
    return _connector


def get_aiohttp_session() -> aiohttp.ClientSession:
    """
    Get the aiohttp ClientSession with a configured connector and timeout.
    :return: aiohttp.ClientSession instance
    """
    global _session  # pylint: disable=global-statement
    if _session is None:
        settings = get_app_settings()
        timeout = aiohttp.ClientTimeout(total=settings.http_client_timeout_total)
        _session = aiohttp.ClientSession(
            connector=get_aiohttp_connector(),
            timeout=timeout,
        )
    return _session


async def close():
    """
    Close the aiohttp session and connector if they are open.
    :return:
    """
    global _session, _connector  # pylint: disable=global-statement
    if _session is not None:
        await _session.close()
        _session = None
    if _connector is not None:
        await _connector.close()
        _connector = None
