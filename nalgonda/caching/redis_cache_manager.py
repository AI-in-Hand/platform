import pickle

from agency_swarm import Agency
from agency_swarm.util import get_openai_client
from redis import asyncio as aioredis

from nalgonda.caching.cache_manager import CacheManager


class RedisCacheManager(CacheManager):
    """Redis cache manager
    This class implements the CacheManager interface using Redis as the cache backend.
    """

    def __init__(self, redis: aioredis.Redis) -> None:
        """Initializes the Redis cache manager"""
        self.redis = redis

    # def __del__(self):
    #     """Closes the Redis connection"""
    #     asyncio.create_task(self.close())

    async def get(self, key: str) -> Agency | None:
        """Gets the value for the given key from the cache"""
        serialized_data = await self.redis.get(key)
        if not serialized_data:
            return None

        loaded = pickle.loads(serialized_data)
        loaded = self.restore_client_objects(loaded)
        return loaded

    async def set(self, key: str, value: Agency) -> None:
        """Sets the value for the given key in the cache"""
        value_copy = self.remove_client_objects(value)
        serialized_data = pickle.dumps(value_copy)
        await self.redis.set(key, serialized_data)

    async def delete(self, key: str) -> None:
        """Deletes the value for the given key from the cache"""
        await self.redis.delete(key)

    async def close(self) -> None:
        """Closes the Redis connection"""
        await self.redis.close()

    def remove_client_objects(self, agency: Agency) -> Agency:
        """Remove all client objects from the agency object"""
        for agent in agency.agents:
            agent.client = None

        agency.main_thread.client = None

        return agency

    def restore_client_objects(self, agency: Agency) -> Agency:
        """Restore all client objects from the agency object"""
        for agent in agency.agents:
            agent.client = get_openai_client()

        agency.main_thread.client = get_openai_client()

        return agency
