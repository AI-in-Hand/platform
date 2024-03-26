from fastapi import Depends
from redis import asyncio as aioredis

from backend.repositories.agency_config_firestore_storage import AgencyConfigFirestoreStorage
from backend.repositories.agent_config_firestore_storage import AgentConfigFirestoreStorage
from backend.repositories.env_config_firestore_storage import EnvConfigFirestoreStorage
from backend.repositories.session_firestore_storage import SessionConfigFirestoreStorage
from backend.services.agency_manager import AgencyManager
from backend.services.agent_manager import AgentManager
from backend.services.caching.redis_cache_manager import RedisCacheManager
from backend.services.env_config_manager import EnvConfigManager
from backend.services.session_manager import SessionManager
from backend.settings import settings


def get_redis() -> aioredis.Redis:
    redis_url = str(settings.redis_tls_url or settings.redis_url)
    redis = aioredis.from_url(redis_url, decode_responses=False, ssl_cert_reqs="none")
    return redis


def get_redis_cache_manager(redis: aioredis.Redis = Depends(get_redis)) -> RedisCacheManager:
    return RedisCacheManager(redis)


def get_env_config_manager(
    env_config_storage: EnvConfigFirestoreStorage = Depends(EnvConfigFirestoreStorage),
) -> EnvConfigManager:
    return EnvConfigManager(env_config_storage)


def get_agent_manager(
    storage: AgentConfigFirestoreStorage = Depends(AgentConfigFirestoreStorage),
    env_config_manager: EnvConfigManager = Depends(get_env_config_manager),
) -> AgentManager:
    return AgentManager(storage, env_config_manager)


def get_agency_manager(
    cache_manager: RedisCacheManager = Depends(get_redis_cache_manager),
    agent_manager: AgentManager = Depends(get_agent_manager),
    agency_config_storage: AgencyConfigFirestoreStorage = Depends(AgencyConfigFirestoreStorage),
    env_config_manager: EnvConfigManager = Depends(get_env_config_manager),
) -> AgencyManager:
    return AgencyManager(cache_manager, agent_manager, agency_config_storage, env_config_manager)


def get_session_manager(
    session_storage: SessionConfigFirestoreStorage = Depends(SessionConfigFirestoreStorage),
    env_config_manager: EnvConfigManager = Depends(get_env_config_manager),
) -> SessionManager:
    """Returns a SessionManager object"""
    return SessionManager(session_storage=session_storage, env_config_manager=env_config_manager)