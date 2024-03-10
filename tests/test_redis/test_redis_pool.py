"""Tests for the Person model."""

from app.redis.redis_pool import RedisPool


def test_redis_pool_singleton():
    """
    Test that RedisPool is a singleton
    """

    pool1 = RedisPool()
    pool2 = RedisPool()
    assert pool1 is pool2
