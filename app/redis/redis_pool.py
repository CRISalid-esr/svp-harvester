import aioredis
from loguru import logger

from app.config import get_app_settings


class RedisPool:
    _instance = None

    class Connexion:
        """
        Context manager for aioredis connection
        """

        def __init__(self, conn: aioredis.Redis):
            self.conn = conn

        async def __aenter__(self) -> aioredis.Redis:
            return self.conn

        async def __aexit__(self, exc_type, exc_val, exc_tb):
            await self.conn.close()

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        settings = get_app_settings()
        if not hasattr(self, "pool"):
            logger.info(
                f"Instanciating RedisPool Singleton at URL {settings.redis_url} "
                f"with {settings.redis_max_connections} max connections"
            )
            self.pool = aioredis.ConnectionPool.from_url(
                settings.redis_url, max_connections=settings.redis_max_connections
            )

    def get_connection(self) -> aioredis.Redis:
        return RedisPool.Connexion(conn=aioredis.Redis(connection_pool=self.pool))

    async def check_ready(self) -> bool:
        try:
            async with self.get_connection() as conn:
                await conn.ping()
                return True
        except aioredis.exceptions.ConnectionError:
            return False
