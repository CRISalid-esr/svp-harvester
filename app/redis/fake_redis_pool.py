# pylint: disable=duplicate-code
class FakeRedisPool:
    """
    Fake RedisPool singleton that always returns None for get() operations.
    Useful in tests.
    """

    _instance = None

    class FakeRedis:
        """
        Fake Redis client that simulates a Redis connection.
        """

        async def get(self, name=None):  # pylint: disable=unused-argument
            """
            Simulate a Redis get operation.
            :param name:
            :return:
            """
            return None

        async def ping(self):
            """
            Simulate a Redis ping operation.
            :return:
            """
            return True  # Optional: let ping pass if check_ready() is used

        async def close(self):
            """
            Simulate closing the Redis connection.
            :return:
            """

        async def set(self, name, value, ex=None):  # pylint: disable=unused-argument
            """
            Simulate a Redis set operation.
            :param name:
            :param value:
            :param ex:
            :return:
            """

    class Connexion:
        """
        Context manager for the fake Redis connection.
        """

        def __init__(self):
            self.conn = FakeRedisPool.FakeRedis()

        async def __aenter__(self):
            return self.conn

        async def __aexit__(self, exc_type, exc_val, exc_tb):
            await self.conn.close()

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls, *args, **kwargs)
        return cls._instance

    def get_connection(self):
        """
        Get a fake Redis connection.
        :return:
        """
        return FakeRedisPool.Connexion()

    async def check_ready(self) -> bool:
        """
        Check if the Redis connection is ready.
        :return:
        """
        return True  # Simulate that Redis is always ready
