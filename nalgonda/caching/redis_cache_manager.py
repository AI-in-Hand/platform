import pickle

from agency_swarm import Agency
from redis import asyncio as aioredis

from nalgonda.caching.cache_manager import CacheManager
from nalgonda.settings import settings


class RedisCacheManager(CacheManager):
    def __init__(self):
        self.redis = aioredis.from_url(settings.redis_url, decode_responses=True)

    async def get(self, key: str) -> Agency | None:
        serialized_data = await self.redis.get(key)
        return pickle.loads(serialized_data) if serialized_data else None

    async def set(self, key: str, value: Agency) -> None:
        serialized_data = pickle.dumps(value)
        await self.redis.set(key, serialized_data)

    async def delete(self, key: str) -> None:
        await self.redis.delete(key)

    async def close(self) -> None:
        await self.redis.close()
