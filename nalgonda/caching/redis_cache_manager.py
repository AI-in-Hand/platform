import asyncio
import pickle
from ssl import CERT_NONE

from agency_swarm import Agency
from agency_swarm.util import get_openai_client
from redis import asyncio as aioredis

from nalgonda.caching.cache_manager import CacheManager
from nalgonda.settings import settings


class RedisCacheManager(CacheManager):
    """Redis cache manager
    This class implements the CacheManager interface using Redis as the cache backend.
    """

    def __init__(self):
        """Initializes the Redis cache manager"""
        redis_url = str(settings.redis_tls_url or settings.redis_url)
        self.redis = aioredis.from_url(redis_url, decode_responses=True, ssl_cert_reqs="none")

    def __del__(self):
        """Wait for the Redis connection to close"""
        asyncio.run(self.close())

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

    @staticmethod
    def remove_client_objects(agency: Agency) -> Agency:
        """Remove all client objects from the agency object"""
        for agent in agency.agents:
            agent.client = None

        agency.main_thread.client = None

        return agency

    @staticmethod
    def restore_client_objects(agency: Agency) -> Agency:
        """Restore all client objects from the agency object"""
        for agent in agency.agents:
            agent.client = get_openai_client()

        agency.main_thread.client = get_openai_client()

        return agency
