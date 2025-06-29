import asyncio
import gc
from typing import Optional

import aiohttp
from loguru import logger

from app.config import get_app_settings


class AioHttpClientManager:
    """
    A singleton manager for aiohttp ClientSession and TCPConnector.
    """

    _connector: Optional[aiohttp.TCPConnector] = None
    _session: Optional[aiohttp.ClientSession] = None
    _lock = asyncio.Lock()
    _usage_counter = 0
    _renew_threshold = 1000
    _grace_period = 300  # seconds

    @classmethod
    async def get_session(cls) -> aiohttp.ClientSession:
        """
        Get the aiohttp ClientSession with a configured connector and timeout.
        The session is renewed after a fixed usage threshold, and the old one is
        closed after a grace period.
        :return: aiohttp.ClientSession instance
        """
        async with cls._lock:
            if cls._session is None or cls._session.closed:
                await cls._init()

            cls._usage_counter += 1
            logger.debug(f"aiohttp usage counter (session): {cls._usage_counter}")

            if cls._usage_counter >= cls._renew_threshold:
                logger.debug(
                    f"Renewing aiohttp session after {cls._usage_counter} requests"
                )
                old_session = cls._session
                old_connector = cls._connector
                asyncio.create_task(cls._schedule_cleanup(old_session, old_connector))
                await cls._init()
                cls._usage_counter = 0

            return cls._session

    @classmethod
    async def get_connector(cls) -> aiohttp.TCPConnector:
        """
        Get the aiohttp TCP connector with configured limits and DNS cache TTL.
        If uninitialized, it is created.
        :return: aiohttp.TCPConnector instance
        """
        async with cls._lock:
            if cls._connector is None or cls._connector.closed:
                await cls._init()

            cls._usage_counter += 1
            logger.debug(f"aiohttp usage counter (connector): {cls._usage_counter}")

            if cls._usage_counter >= cls._renew_threshold:
                logger.debug(
                    f"Renewing aiohttp session after {cls._usage_counter} requests"
                )
                old_session = cls._session
                old_connector = cls._connector
                asyncio.create_task(cls._schedule_cleanup(old_session, old_connector))
                await cls._init()
                cls._usage_counter = 0

            return cls._connector

    @classmethod
    async def _init(cls):
        settings = get_app_settings()
        cls._connector = aiohttp.TCPConnector(
            limit=settings.http_client_limit,
            ttl_dns_cache=settings.http_client_ttl_dns_cache,
            enable_cleanup_closed=False,
        )
        cls._session = aiohttp.ClientSession(
            connector=cls._connector,
            timeout=aiohttp.ClientTimeout(total=settings.http_client_timeout_total),
        )

    @classmethod
    async def _schedule_cleanup(
        cls,
        session: Optional[aiohttp.ClientSession],
        connector: Optional[aiohttp.TCPConnector],
    ):
        await asyncio.sleep(cls._grace_period)
        try:
            if session is not None and not session.closed:
                await session.close()
            if connector is not None and not connector.closed:
                await connector.close()
            gc.collect()
            logger.debug(
                f"Closed aiohttp session and connector: {session}, {connector}"
            )
        except Exception:  # pylint: disable=broad-exception-caught
            logger.debug(f"Error during aiohttp cleanup: {session}, {connector}")

    @classmethod
    async def close(cls):
        """
        Close the aiohttp session and connector if they are open.
        """
        async with cls._lock:
            if cls._session:
                await cls._session.close()
            if cls._connector:
                await cls._connector.close()
            cls._session = None
            cls._connector = None
            cls._usage_counter = 0
