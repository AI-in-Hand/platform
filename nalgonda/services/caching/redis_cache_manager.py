import pickle

from agency_swarm import Agency
from redis import Redis

from nalgonda.constants import DEFAULT_CACHE_EXPIRATION
from nalgonda.services.caching.cache_manager import CacheManager


class RedisCacheManager(CacheManager):
    """Redis cache manager
    This class implements the CacheManager interface using Redis as the cache backend.
    """

    def __init__(self, redis: Redis) -> None:
        """Initializes the Redis cache manager"""
        self.redis = redis

    def get(self, key: str) -> Agency | None:
        """Gets the value for the given key from the cache"""
        serialized_data: bytes = self.redis.get(key)  # type: ignore
        if not serialized_data:
            return None

        loaded = pickle.loads(serialized_data)
        return loaded

    def set(self, key: str, value: Agency, expire: int = DEFAULT_CACHE_EXPIRATION) -> None:
        """Sets the value for the given key in the cache"""
        serialized_data = pickle.dumps(value)
        self.redis.set(key, serialized_data, ex=expire)

    def delete(self, key: str) -> None:
        """Deletes the value for the given key from the cache"""
        self.redis.delete(key)

    def close(self) -> None:
        """Closes the Redis connection"""
        self.redis.close()
