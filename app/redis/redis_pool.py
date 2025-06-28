import redis.asyncio as redis
from loguru import logger

from app.config import get_app_settings


class RedisPool:
    """
    Singleton for redis.asyncio connection pool
    """

    _instance = None

    class Connexion:
        """
        Context manager for Redis connection
        """

        def __init__(self, conn: redis.Redis):
            self.conn = conn

        async def __aenter__(self) -> redis.Redis:
            return self.conn

        async def __aexit__(self, exc_type, exc_val, exc_tb):
            # Don't close the whole pool; only disconnect if needed
            await self.conn.close()

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        settings = get_app_settings()
        if not hasattr(self, "pool"):
            logger.info(
                f"Instantiating RedisPool Singleton at URL {settings.redis_url} "
                f"with {settings.redis_max_connections} max connections"
            )
            self.pool = redis.ConnectionPool.from_url(
                settings.redis_url,
                max_connections=settings.redis_max_connections,
                decode_responses=False,
            )

    def get_connection(self) -> redis.Redis:
        """
        Get a Redis connection from the pool.
        :return: Redis connection wrapped in a context manager.
        """
        return RedisPool.Connexion(conn=redis.Redis(connection_pool=self.pool))

    async def check_ready(self) -> bool:
        """
        Check if the Redis connection is ready.
        :return: bool: True if the connection is ready, False otherwise.
        """
        try:
            async with self.get_connection() as conn:
                await conn.ping()
                return True
        except ConnectionError:
            return False
