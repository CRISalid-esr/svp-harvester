from asyncio import Lock
from typing import Optional

import aiohttp

from app.config import get_app_settings


class AioHttpClientManager:
    """
    Manages a shared aiohttp ClientSession and TCPConnector for the application.
    """

    _connector: Optional[aiohttp.TCPConnector] = None
    _session: Optional[aiohttp.ClientSession] = None
    _lock: Lock = Lock()

    @classmethod
    async def get_connector(cls) -> aiohttp.TCPConnector:
        """
        Get the aiohttp TCP connector, creating it if it does not exist.
        :return:
        """
        if cls._connector is not None:
            return cls._connector

        settings = get_app_settings()
        cls._connector = aiohttp.TCPConnector(
            limit=settings.http_client_limit,
            ttl_dns_cache=settings.http_client_ttl_dns_cache,
        )
        return cls._connector

    @classmethod
    async def get_session(cls) -> aiohttp.ClientSession:
        """
        Get the aiohttp ClientSession, creating it if it does not exist or is closed.
        :return:
        """
        if cls._session is not None and not cls._session.closed:
            return cls._session

        async with cls._lock:
            if cls._session is None or cls._session.closed:
                settings = get_app_settings()
                timeout = aiohttp.ClientTimeout(
                    total=settings.http_client_timeout_total
                )
                connector = await cls.get_connector()
                cls._session = aiohttp.ClientSession(
                    connector=connector,
                    timeout=timeout,
                )
        return cls._session

    @classmethod
    async def close(cls):
        """
        Close the aiohttp ClientSession and TCPConnector gracefully.
        :return:
        """
        if cls._session is not None:
            await cls._session.close()
            cls._session = None

        if cls._connector is not None:
            await cls._connector.close()
            cls._connector = None
