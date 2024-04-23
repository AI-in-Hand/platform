import pickle
from typing import Any

from redis import asyncio as aioredis

from backend.constants import DEFAULT_CACHE_EXPIRATION


class RedisCacheManager:
    """Redis cache manager
    This class implements the CacheManager interface using Redis as the cache backend.
    """

    def __init__(self, redis: aioredis.Redis) -> None:
        """Initializes the Redis cache manager"""
        self.redis = redis

    async def get(self, key: str) -> Any | None:
        """Gets the value for the given key from the cache"""
        serialized_data = await self.redis.get(key)
        if not serialized_data:
            return None

        loaded = pickle.loads(serialized_data)
        return loaded

    async def set(self, key: str, value: Any, expire: int = DEFAULT_CACHE_EXPIRATION) -> None:
        """Sets the value for the given key in the cache"""
        serialized_data = pickle.dumps(value)
        await self.redis.set(key, serialized_data, ex=expire)

    async def delete(self, key: str) -> None:
        """Deletes the value for the given key from the cache"""
        await self.redis.delete(key)

    async def close(self) -> None:
        """Closes the Redis connection"""
        await self.redis.close()
