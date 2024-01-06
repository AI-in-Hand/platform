import asyncio
import logging
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
        """Create the agency. If agency_id is not provided, it will be generated.
        If agency_id is provided, it will be used to load the agency from the firestore.
        If agency is not found in the firestore, it will be created.
        """
        agency_id = agency_id or uuid.uuid4().hex

        agency_config_storage = AgencyConfigFirestoreStorage(agency_id)
        agency_config = await asyncio.to_thread(agency_config_storage.load)

        if not agency_config:
            # Create the agency config if it does not exist
            agency_config = await asyncio.to_thread(agency_config_storage.load_or_create)

        agents = await self.load_and_construct_agents(agency_config)
        agency = self.construct_agency(agency_config, agents)

        await self.cache_agency(agency, agency_id, None)
        return agency, agency_id

    async def get_agency(self, agency_id: str, thread_id: str | None = None) -> Agency | None:
        cache_key = self.get_cache_key(agency_id, thread_id)
        agency = await self.cache_manager.get(cache_key)
        if not agency:
            # If agency is not found in the cache, re-populate the cache
            agency = await self.repopulate_cache(agency_id)
            if not agency:
                logger.error(f"Agency configuration for {agency_id} could not be found in the Firestore database.")
                return None

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
        cache_key = self.get_cache_key(agency_id)
        agency_config_storage = AgencyConfigFirestoreStorage(agency_id)
        agency_config = await asyncio.to_thread(agency_config_storage.load)
        if not agency_config:
            logger.error(f"Agency with id {agency_id} not found.")
            return None

        agents = await self.load_and_construct_agents(agency_config)
        agency = self.construct_agency(agency_config, agents)
        await self.cache_manager.set(cache_key, agency)
        return agency

    async def cache_agency(self, agency: Agency, agency_id: str, thread_id: str | None) -> None:
        """Cache the agency."""
        cache_key = self.get_cache_key(agency_id, thread_id)

        await self.cache_manager.set(cache_key, agency)

    async def delete_agency_from_cache(self, agency_id: str, thread_id: str | None) -> None:
        """Delete the agency from the cache."""
        cache_key = self.get_cache_key(agency_id, thread_id)

        await self.cache_manager.delete(cache_key)

    @staticmethod
    async def load_and_construct_agents(agency_config: AgencyConfig) -> dict[str, Agent]:
        agents = {}
        for agent_id in agency_config.agents:
            agent_config_storage = AgentConfigFirestoreStorage(agent_id)
            agent_config = await asyncio.to_thread(agent_config_storage.load)
            if agent_config:
                agent = Agent(
                    id=agent_config.id,
                    name=f"{agent_config.role}_{agency_config.agency_id}",
                    description=agent_config.description,
                    instructions=agent_config.instructions,
                    files_folder=agent_config.files_folder,
                    tools=[TOOL_MAPPING[tool] for tool in agent_config.tools],
                )
                agents[agent_config.role] = agent
                agent_config.id = agent.id
                await asyncio.to_thread(agent_config_storage.save, agent_config)
        return agents

    @staticmethod
    def construct_agency(agency_config: AgencyConfig, agents: dict[str, Agent]) -> Agency:
        """Create the agency using external library agency-swarm. It is a wrapper around OpenAI API.
        It saves all the settings in the settings.json file (in the root folder, not thread safe)
        """
        agency_chart = [
            [agents[role] for role in layer] if isinstance(layer, list) else agents[layer]
            for layer in agency_config.agency_chart
        ]
        return Agency(agency_chart, shared_instructions=agency_config.agency_manifesto)

    @staticmethod
    def get_cache_key(agency_id: str, thread_id: str | None = None) -> str:
        return f"{agency_id}/{thread_id}" if thread_id else agency_id


def get_agency_manager(redis: aioredis.Redis = Depends(get_redis)) -> AgencyManager:
    return AgencyManager(redis)
