import pickle
from typing import Any

import aioredis
from loguru import logger

from app.config import get_app_settings
from app.redis.redis_pool import RedisPool


class ThirdApiCache:
    """
    Cache provider with time to live for third party API results
    """

    @staticmethod
    async def get(api_name: str, key: str) -> Any:
        """
        Get a value from the cache
        :param api_name: name of the API, used as a prefix for the key
            and to retrieve the caching duration from settings
        :param key: key to retrieve the value from the cache
        :return: an unmarshalled value from the cache, or None if not found
        """
        settings = get_app_settings()
        if not settings.third_api_caching_enabled:
            return None
        try:
            async with RedisPool().get_connection() as conn:
                value = await conn.get(name=f"{api_name}:{key}")
                if value:
                    try:
                        return pickle.loads(value)
                    except pickle.UnpicklingError:
                        logger.error(
                            f"Cannot unpickle value from Redis for {api_name}:{key}, "
                            f"will not use it"
                        )
                        return None
        except aioredis.exceptions.ConnectionError as e:
            logger.error(
                f"Cannot connect to Redis cache (with error {e}),"
                f"aborting cache retrieval for {api_name}:{key}"
            )
            return None

    @staticmethod
    async def set(api_name: str, key: str, value: Any) -> None:
        settings = get_app_settings()
        if not settings.third_api_caching_enabled:
            return None
        try:
            expiration_time = getattr(settings, f"{api_name}_caching_duration")
        except AttributeError:
            logger.error(
                f"Cannot find caching duration for {api_name}, will use default value"
                f"please set {api_name}_caching_duration in settings"
                f"or in uppercase {api_name.upper()}_CACHING_DURATION in environment variables"
                f"to avoid this error in the future"
            )
            expiration_time = settings.third_api_default_caching_duration
        try:
            serialized_value = pickle.dumps(value)
        except pickle.PicklingError:
            logger.error(
                f"Cannot pickle value to Redis for {api_name}:{key}, will not cache it"
            )
            return
        async with RedisPool().get_connection() as conn:
            await conn.set(name=f"{api_name}:{key}", value=serialized_value)
            await conn.expire(name=f"{api_name}:{key}", time=expiration_time)
