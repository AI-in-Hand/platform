from fastapi import Depends
from redis import asyncio as aioredis

from backend.repositories.agency_config_storage import AgencyConfigStorage
from backend.repositories.agent_flow_spec_storage import AgentFlowSpecStorage
from backend.repositories.session_storage import SessionConfigStorage
from backend.repositories.skill_config_storage import SkillConfigStorage
from backend.repositories.user_secret_storage import UserSecretStorage
from backend.services.adapters.agency_adapter import AgencyAdapter
from backend.services.adapters.agent_adapter import AgentAdapter
from backend.services.adapters.session_adapter import SessionAdapter
from backend.services.agency_manager import AgencyManager
from backend.services.agent_manager import AgentManager
from backend.services.caching.redis_cache_manager import RedisCacheManager
from backend.services.session_manager import SessionManager
from backend.services.skill_manager import SkillManager
from backend.services.user_secret_manager import UserSecretManager
from backend.settings import settings


def get_redis() -> aioredis.Redis:
    redis_url = str(settings.redis_tls_url or settings.redis_url)
    redis = aioredis.from_url(redis_url, decode_responses=False, ssl_cert_reqs="none")
    return redis


def get_redis_cache_manager(redis: aioredis.Redis = Depends(get_redis)) -> RedisCacheManager:
    return RedisCacheManager(redis)


def get_user_secret_manager(
    user_secret_storage: UserSecretStorage = Depends(UserSecretStorage),
) -> UserSecretManager:
    return UserSecretManager(user_secret_storage)


def get_skill_manager(
    storage: SkillConfigStorage = Depends(SkillConfigStorage),
) -> SkillManager:
    return SkillManager(storage)


def get_agent_manager(
    storage: AgentFlowSpecStorage = Depends(AgentFlowSpecStorage),
    user_secret_manager: UserSecretManager = Depends(get_user_secret_manager),
    skill_storage: SkillConfigStorage = Depends(SkillConfigStorage),
) -> AgentManager:
    return AgentManager(storage, user_secret_manager, skill_storage)


def get_agency_manager(
    agent_manager: AgentManager = Depends(get_agent_manager),
    agency_config_storage: AgencyConfigStorage = Depends(AgencyConfigStorage),
    user_secret_manager: UserSecretManager = Depends(get_user_secret_manager),
) -> AgencyManager:
    return AgencyManager(agent_manager, agency_config_storage, user_secret_manager)


def get_session_manager(
    session_storage: SessionConfigStorage = Depends(SessionConfigStorage),
    user_secret_manager: UserSecretManager = Depends(get_user_secret_manager),
) -> SessionManager:
    """Returns a SessionManager object"""
    return SessionManager(session_storage=session_storage, user_secret_manager=user_secret_manager)


def get_agent_adapter(
    skill_config_storage: SkillConfigStorage = Depends(SkillConfigStorage),
) -> AgentAdapter:
    return AgentAdapter(skill_config_storage)


def get_agency_adapter(
    agent_flow_spec_storage: AgentFlowSpecStorage = Depends(AgentFlowSpecStorage),
    agent_adapter: AgentAdapter = Depends(get_agent_adapter),
) -> AgencyAdapter:
    return AgencyAdapter(agent_flow_spec_storage, agent_adapter)


def get_session_adapter(
    agency_config_storage: AgencyConfigStorage = Depends(AgencyConfigStorage),
    agency_adapter: AgencyAdapter = Depends(get_agency_adapter),
) -> SessionAdapter:
    return SessionAdapter(agency_config_storage, agency_adapter)
