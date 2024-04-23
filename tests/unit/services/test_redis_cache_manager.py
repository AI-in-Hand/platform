import pickle
from unittest.mock import AsyncMock

import pytest
from redis import asyncio as aioredis

from backend.constants import DEFAULT_CACHE_EXPIRATION
from backend.services.redis_cache_manager import RedisCacheManager


@pytest.fixture
def redis_mock():
    redis_client_mock = AsyncMock(spec=aioredis.Redis)
    redis_client_mock.get = AsyncMock(return_value=pickle.dumps("value"))
    redis_client_mock.set = AsyncMock()
    redis_client_mock.delete = AsyncMock()
    redis_client_mock.close = AsyncMock()
    return redis_client_mock


@pytest.fixture
def cache_manager(redis_mock):
    return RedisCacheManager(redis_mock)


@pytest.mark.asyncio
async def test_get_existing_key(cache_manager, redis_mock):
    result = await cache_manager.get("key")
    assert result == "value"
    redis_mock.get.assert_called_once_with("key")


@pytest.mark.asyncio
async def test_get_non_existing_key(cache_manager, redis_mock):
    redis_mock.get.return_value = None
    result = await cache_manager.get("key")
    assert result is None
    redis_mock.get.assert_called_once_with("key")


@pytest.mark.asyncio
async def test_get_invalid_data(cache_manager, redis_mock):
    # Test getting invalid data from the cache
    redis_mock.get.return_value = b"invalid_data"
    with pytest.raises(pickle.UnpicklingError):
        await cache_manager.get("key")
    redis_mock.get.assert_called_once_with("key")


@pytest.mark.asyncio
async def test_get_empty_value(cache_manager, redis_mock):
    # Test getting an empty value from the cache
    redis_mock.get.return_value = pickle.dumps("")
    result = await cache_manager.get("key")
    assert result == ""
    redis_mock.get.assert_called_once_with("key")


@pytest.mark.asyncio
async def test_set(cache_manager, redis_mock):
    await cache_manager.set("key", "value", expire=60)
    redis_mock.set.assert_called_once_with("key", pickle.dumps("value"), ex=60)


@pytest.mark.asyncio
async def test_set_default_expiration(cache_manager, redis_mock):
    await cache_manager.set("key", "value")
    redis_mock.set.assert_called_once_with("key", pickle.dumps("value"), ex=DEFAULT_CACHE_EXPIRATION)


@pytest.mark.asyncio
async def test_set_empty_value(cache_manager, redis_mock):
    # Test setting an empty value in the cache
    await cache_manager.set("key", "")
    redis_mock.set.assert_called_once_with("key", pickle.dumps(""), ex=DEFAULT_CACHE_EXPIRATION)


@pytest.mark.asyncio
async def test_delete(cache_manager, redis_mock):
    await cache_manager.delete("key")
    redis_mock.delete.assert_called_once_with("key")


@pytest.mark.asyncio
async def test_delete_non_existing_key(cache_manager, redis_mock):
    # Test deleting a non-existing key from the cache
    await cache_manager.delete("non_existing_key")
    redis_mock.delete.assert_called_once_with("non_existing_key")


@pytest.mark.asyncio
async def test_close(cache_manager, redis_mock):
    await cache_manager.close()
    redis_mock.close.assert_called_once()
