import asyncio
import logging
from copy import deepcopy
from uuid import uuid4

from agency_swarm import Agency, Agent
from agency_swarm.util import get_openai_client
from fastapi import Depends
from redis import asyncio as aioredis

from nalgonda.dependencies.agent_manager import AgentManager, get_agent_manager
from nalgonda.dependencies.caching.redis_cache_manager import RedisCacheManager
from nalgonda.dependencies.redis import get_redis
from nalgonda.models.agency_config import AgencyConfig
from nalgonda.persistence.agency_config_firestore_storage import AgencyConfigFirestoreStorage

logger = logging.getLogger(__name__)


class AgencyManager:
    def __init__(self, redis: aioredis.Redis, agent_manager: AgentManager) -> None:
        self.cache_manager = RedisCacheManager(redis)
        self.agent_manager = agent_manager

    async def create_agency(self, agency_id: str | None = None) -> str:
        """Create the agency. If agency_id is not provided, it will be generated.
        If agency_id is provided, it will be used to load the agency from the firestore.
        If agency is not found in the firestore, it will be created.
        """
        agency_id = agency_id or str(uuid4())

        agency_config_storage = AgencyConfigFirestoreStorage(agency_id)
        agency_config = await asyncio.to_thread(agency_config_storage.load_or_create)

        agents = await self.load_and_construct_agents(agency_config)
        agency = await asyncio.to_thread(self.construct_agency, agency_config, agents)

        await self.cache_agency(agency, agency_id, None)
        return agency_id

    async def get_agency(self, agency_id: str, thread_id: str | None = None) -> Agency | None:
        cache_key = self.get_cache_key(agency_id, thread_id)
        agency = await self.cache_manager.get(cache_key)

        if not agency:
            # If agency is not found in the cache, re-populate the cache
            agency = await self.repopulate_cache(agency_id)
            if not agency:
                logger.error(f"Agency configuration for {agency_id} could not be found in the Firestore database.")
                return None

        agency = self._restore_client_objects(agency)
        return agency

    async def update_agency(self, agency_config: AgencyConfig, updated_data: dict) -> None:
        """Update the agency. It will update the agency in the firestore and also in the cache."""
        agency_id = agency_config.agency_id

        updated_data.pop("agency_id", None)  # ensure agency_id is not modified
        agency_config.update(updated_data)
        agency_config_storage = AgencyConfigFirestoreStorage(agency_id)
        await asyncio.to_thread(agency_config_storage.save, agency_config)

        # Update the agency in the cache
        await self.repopulate_cache(agency_id)

    async def repopulate_cache(self, agency_id: str) -> Agency | None:
        agency_config_storage = AgencyConfigFirestoreStorage(agency_id)
        agency_config = await asyncio.to_thread(agency_config_storage.load)
        if not agency_config:
            logger.error(f"Agency with id {agency_id} not found.")
            return None

        agents = await self.load_and_construct_agents(agency_config)
        agency = await asyncio.to_thread(self.construct_agency, agency_config, agents)

        await self.cache_agency(agency, agency_id, None)
        return agency

    async def load_and_construct_agents(self, agency_config: AgencyConfig) -> dict[str, Agent]:
        agents = {}
        for agent_id in agency_config.agents:
            get_result = await self.agent_manager.get_agent(agent_id)
            if get_result:
                agent, agent_config = get_result
                agents[agent_config.name] = agent
            else:
                logger.error(f"Agent with id {agent_id} not found.")
                # TODO: Handle this error (raise exception?)
        return agents

    @staticmethod
    def construct_agency(agency_config: AgencyConfig, agents: dict[str, Agent]) -> Agency:
        """Create the agency using external library agency-swarm. It is a wrapper around OpenAI API.
        It saves all the settings in the settings.json file (in the root folder, not thread safe)
        """
        agency_chart = []
        if agents and agency_config.main_agent:
            main_agent = agents[agency_config.main_agent]
            agency_chart = [main_agent]
            if agency_config.agency_chart:
                new_agency_chart = [[agents[name] for name in layer] for layer in agency_config.agency_chart]
                agency_chart.extend(new_agency_chart)

        return Agency(agency_chart, shared_instructions=agency_config.agency_manifesto)

    async def cache_agency(self, agency: Agency, agency_id: str, thread_id: str | None) -> None:
        """Cache the agency."""
        cache_key = self.get_cache_key(agency_id, thread_id)
        agency_clean = self._remove_client_objects(agency)
        await self.cache_manager.set(cache_key, agency_clean)

    async def delete_agency_from_cache(self, agency_id: str, thread_id: str | None) -> None:
        """Delete the agency from the cache."""
        cache_key = self.get_cache_key(agency_id, thread_id)

        await self.cache_manager.delete(cache_key)

    @staticmethod
    def get_cache_key(agency_id: str, thread_id: str | None = None) -> str:
        return f"{agency_id}/{thread_id}" if thread_id else agency_id

    @staticmethod
    def _remove_client_objects(agency: Agency) -> Agency:
        """Remove all client objects from the agency object"""
        agency = deepcopy(agency)
        for agent in agency.agents:
            agent.client = None
        agency.main_thread.client = None
        return agency

    @staticmethod
    def _restore_client_objects(agency: Agency) -> Agency:
        """Restore all client objects from the agency object"""
        for agent in agency.agents:
            agent.client = get_openai_client()
        agency.main_thread.client = get_openai_client()
        return agency


def get_agency_manager(
    redis: aioredis.Redis = Depends(get_redis), agent_manager: AgentManager = Depends(get_agent_manager)
) -> AgencyManager:
    return AgencyManager(redis, agent_manager)
