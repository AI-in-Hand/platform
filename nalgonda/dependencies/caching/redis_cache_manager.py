import pickle

from agency_swarm import Agency
from fastapi import Depends
from redis import asyncio as aioredis

from nalgonda.constants import DEFAULT_CACHE_EXPIRATION
from nalgonda.dependencies.caching.cache_manager import CacheManager
from nalgonda.dependencies.redis import get_redis


class RedisCacheManager(CacheManager):
    """Redis cache manager
    This class implements the CacheManager interface using Redis as the cache backend.
    """

    def __init__(self, redis: aioredis.Redis) -> None:
        """Initializes the Redis cache manager"""
        self.redis = redis

    async def get(self, key: str) -> Agency | None:
        """Gets the value for the given key from the cache"""
        serialized_data = await self.redis.get(key)
        if not serialized_data:
            return None

        loaded = pickle.loads(serialized_data)
        return loaded

    async def set(self, key: str, value: Agency, expire: int = DEFAULT_CACHE_EXPIRATION) -> None:
        """Sets the value for the given key in the cache"""
        serialized_data = pickle.dumps(value)
        await self.redis.set(key, serialized_data, ex=expire)

    async def delete(self, key: str) -> None:
        """Deletes the value for the given key from the cache"""
        await self.redis.delete(key)

    async def close(self) -> None:
        """Closes the Redis connection"""
        await self.redis.close()


def get_redis_cache_manager(redis: aioredis.Redis = Depends(get_redis)) -> RedisCacheManager:
    return RedisCacheManager(redis)
