class FakeRedisPool:
    """
    Fake RedisPool singleton that always returns None for get() operations.
    Useful in tests.
    """

    _instance = None

    class FakeRedis:
        async def get(self, name=None):
            return None

        async def ping(self):
            return True  # Optional: let ping pass if check_ready() is used

        async def close(self):
            pass

        async def set(self, name, value, ex=None):
            pass

    class Connexion:
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
        return FakeRedisPool.Connexion()

    async def check_ready(self) -> bool:
        return True  # Simulate that Redis is always ready
