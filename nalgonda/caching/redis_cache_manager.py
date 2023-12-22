import asyncio
import pickle

from agency_swarm import Agency
from redis import asyncio as aioredis

from nalgonda.caching.cache_manager import CacheManager
from nalgonda.settings import settings


class RedisCacheManager(CacheManager):
    """Redis cache manager
    This class implements the CacheManager interface using Redis as the cache backend.
    """

    def __init__(self):
        """Initializes the Redis cache manager"""
        self.redis = aioredis.from_url(str(settings.redis_dsn), decode_responses=True)

    def __del__(self):
        """Wait for the Redis connection to close"""
        asyncio.run(self.close())

    async def get(self, key: str) -> Agency | None:
        """Gets the value for the given key from the cache"""
        serialized_data = await self.redis.get(key)
        return pickle.loads(serialized_data) if serialized_data else None

    async def set(self, key: str, value: Agency) -> None:
        """Sets the value for the given key in the cache"""
        serialized_data = pickle.dumps(value)
        await self.redis.set(key, serialized_data)

    async def delete(self, key: str) -> None:
        """Deletes the value for the given key from the cache"""
        await self.redis.delete(key)

    async def close(self) -> None:
        """Closes the Redis connection"""
        await self.redis.close()
