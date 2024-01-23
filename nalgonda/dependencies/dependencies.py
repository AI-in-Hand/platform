from fastapi import Depends
from redis import Redis, from_url

from nalgonda.persistence.agent_config_firestore_storage import AgentConfigFirestoreStorage
from nalgonda.services.agency_manager import AgencyManager
from nalgonda.services.agent_manager import AgentManager
from nalgonda.services.caching.redis_cache_manager import RedisCacheManager
from nalgonda.services.thread_manager import ThreadManager
from nalgonda.settings import settings


def get_redis() -> Redis:
    redis_url = str(settings.redis_tls_url or settings.redis_url)
    redis = from_url(redis_url, decode_responses=False, ssl_cert_reqs="none")
    return redis


def get_redis_cache_manager(redis: Redis = Depends(get_redis)) -> RedisCacheManager:
    return RedisCacheManager(redis)


def get_agent_manager(storage: AgentConfigFirestoreStorage = Depends(AgentConfigFirestoreStorage)) -> AgentManager:
    return AgentManager(storage)


def get_agency_manager(
    cache_manager: RedisCacheManager = Depends(get_redis_cache_manager),
    agent_manager: AgentManager = Depends(get_agent_manager),
) -> AgencyManager:
    return AgencyManager(cache_manager, agent_manager)


def get_thread_manager() -> ThreadManager:
    """Returns a ThreadManager object"""
    return ThreadManager()
