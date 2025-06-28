from unittest import mock

import pytest
import redis.asyncio as redis  # updated import

PICKLE_ENCODED_ASCII = b"\x80\x04..."  # adjust this to your actual serialized content


@pytest.fixture(name="redis_cache_get_mock")
def fixture_redis_cache_get_mock():
    async def fake_redis_get(name: str):
        if name == "sudoc_publications:https://www.sudoc.fr/070266875.rdf":
            return PICKLE_ENCODED_ASCII
        return None

    return fake_redis_get


@pytest.fixture(name="redis_cache_set_mock")
def fixture_redis_cache_set_mock():
    async def fake_redis_set(name: str, value: bytes):
        pass

    return fake_redis_set


@pytest.fixture(name="redis_cache_expire_mock")
def fixture_redis_cache_expire_mock():
    async def fake_redis_expire(name: str, time: int):
        pass

    return fake_redis_expire


@pytest.fixture(name="redis_cache_mock", autouse=True)
def fixture_redis_cache_mock(
    redis_cache_get_mock, redis_cache_set_mock, redis_cache_expire_mock
):
    with mock.patch.object(redis.Redis, "get") as mock_get, mock.patch.object(
        redis.Redis, "set"
    ) as mock_set, mock.patch.object(redis.Redis, "expire") as mock_expire:
        mock_get.side_effect = redis_cache_get_mock
        mock_set.side_effect = redis_cache_set_mock
        mock_expire.side_effect = redis_cache_expire_mock
        yield mock_get, mock_set, mock_expire
