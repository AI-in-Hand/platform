import asyncio
import logging
import time
import uuid

from agency_swarm import Agency, Agent
from fastapi import Depends
from redis import asyncio as aioredis

from nalgonda.caching.redis_cache_manager import RedisCacheManager
from nalgonda.custom_tools import TOOL_MAPPING
from nalgonda.dependencies.redis import get_redis
from nalgonda.models.agency_config import AgencyConfig
from nalgonda.persistence.agency_config_firestore_storage import AgencyConfigFirestoreStorage
from nalgonda.persistence.agent_config_firestore_storage import AgentConfigFirestoreStorage

logger = logging.getLogger(__name__)


class AgencyManager:
    def __init__(self, redis: aioredis.Redis) -> None:
        self.cache_manager = RedisCacheManager(redis)

    async def create_agency(self, agency_id: str | None = None) -> tuple[Agency, str]:
        """Create an agency and return the agency and the agency_id."""
        agency_id = agency_id or uuid.uuid4().hex

        # Note: Async-to-Sync Bridge
        agency = await asyncio.to_thread(self.load_agency_from_config, agency_id, config=None)
        await self.cache_agency(agency, agency_id, None)
        return agency, agency_id

    async def get_agency(self, agency_id: str, thread_id: str | None) -> Agency | None:
        """Get the agency from the cache. If not found, retrieve from Firestore and repopulate cache."""
        cache_key = self.get_cache_key(agency_id, thread_id)

        agency = await self.cache_manager.get(cache_key)

        if agency is None:
            storage = AgencyConfigFirestoreStorage(agency_id)
            agency_config = storage.load()
            if agency_config:
                agency = await asyncio.to_thread(self.load_agency_from_config, agency_id, config=agency_config)
                await self.cache_manager.set(cache_key, agency)
            else:
                logger.error(f"Agency configuration for {agency_id} could not be found in the Firestore database.")
                return None

        return agency

    async def update_agency(self, agency_config: AgencyConfig, updated_data: dict) -> None:
        """Update the agency"""
        agency_id = agency_config.agency_id

        updated_data.pop("agency_id", None)
        agency_config.update(updated_data)
        agency_config.save()

        agency = await self.get_agency(agency_id, None)
        if not agency:
            agency, _ = await self.create_agency(agency_id)

        await self.cache_agency(agency, agency_id, None)

    async def cache_agency(self, agency: Agency, agency_id: str, thread_id: str | None) -> None:
        """Cache the agency."""
        cache_key = self.get_cache_key(agency_id, thread_id)

        await self.cache_manager.set(cache_key, agency)

    async def delete_agency_from_cache(self, agency_id: str, thread_id: str | None) -> None:
        """Delete the agency from the cache."""
        cache_key = self.get_cache_key(agency_id, thread_id)

        await self.cache_manager.delete(cache_key)

    @staticmethod
    def get_cache_key(agency_id: str, thread_id: str | None) -> str:
        """Get the cache key for the given agency ID and thread ID."""
        return f"{agency_id}/{thread_id}" if thread_id else agency_id

    @staticmethod
    def load_agency_from_config(agency_id: str, config: AgencyConfig | None = None) -> Agency:
        """Load the agency from the config file. The agency is created using the agency-swarm library.

        This code is synchronous and should be run in a single thread.
        The code is currently not thread safe (due to agency-swarm limitations).
        """

        start = time.time()

        # Load agency configuration and related agents
        config = config or AgencyConfig.load_or_create(agency_id)

        _agent_configs = [AgentConfigFirestoreStorage(agent_id).load() for agent_id in config.agents]
        agent_configs = [agent_config for agent_config in _agent_configs if agent_config is not None]

        agents = {
            agent_conf.role: Agent(
                id=agent_conf.id,
                name=f"{agent_conf.role}_{agency_id}",
                description=agent_conf.description,
                instructions=agent_conf.instructions,
                files_folder=agent_conf.files_folder,
                tools=[TOOL_MAPPING[tool] for tool in agent_conf.tools if tool in TOOL_MAPPING],
            )
            for agent_conf in agent_configs
        }

        # Create agency chart based on the config
        agency_chart = [
            [agents[role] for role in chart] if isinstance(chart, list) else agents[chart]
            for chart in config.agency_chart
        ]

        # Create the agency using external library agency-swarm. It is a wrapper around OpenAI API.
        # It saves all the settings in the settings.json file (in the root folder, not thread safe)
        agency = Agency(agency_chart, shared_instructions=config.agency_manifesto)

        # Update agent IDs in the configuration
        for agent_config in agent_configs:
            agent_config.id = agents[agent_config.role].id
            agent_config.save()
        config.save()

        logger.info(f"Agency creation took {time.time() - start} seconds. Session ID: {agency_id}")
        return agency


def update_agent_ids_in_config(agents: list[Agent]) -> None:
    """This function will update the 'id' field for all agents in the agency."""
    for agent in agents:
        storage = AgentConfigFirestoreStorage(agent.id)
        agent_config = storage.load()
        if agent_config:
            agent_config.id = agent.id
            storage.save(agent_config)


def get_agency_manager(redis: aioredis.Redis = Depends(get_redis)) -> AgencyManager:
    """Get the agency manager."""
    return AgencyManager(redis)
