import asyncio
import logging
import time
import uuid

from agency_swarm import Agency, Agent

from nalgonda.caching.redis_cache_manager import RedisCacheManager
from nalgonda.custom_tools import TOOL_MAPPING
from nalgonda.models.agency_config import AgencyConfig

logger = logging.getLogger(__name__)


class AgencyManager:
    def __init__(self) -> None:
        self.cache_manager = RedisCacheManager()

    async def create_agency(self, agency_id: str | None = None) -> tuple[Agency, str]:
        """Create an agency and return the agency and the agency_id."""
        agency_id = agency_id or uuid.uuid4().hex

        # Note: Async-to-Sync Bridge
        agency = await asyncio.to_thread(self.load_agency_from_config, agency_id)
        await self.cache_agency(agency, agency_id, None)
        return agency, agency_id

    async def get_agency(self, agency_id: str, thread_id: str | None) -> Agency | None:
        """Get the agency from the cache."""
        cache_key = self.get_cache_key(agency_id, thread_id)
        agency = await self.cache_manager.get(cache_key)
        return agency

    async def cache_agency(self, agency: Agency, agency_id: str, thread_id: str | None) -> None:
        """Cache the agency."""
        cache_key = self.get_cache_key(agency_id, thread_id)
        await self.cache_manager.set(cache_key, agency)

    async def delete_agency_from_cache(self, agency_id: str, thread_id: str | None) -> None:
        """Delete the agency from the cache."""
        cache_key = self.get_cache_key(agency_id, thread_id)
        await self.cache_manager.delete(cache_key)

    async def refresh_thread_id(self, agency: Agency, agency_id: str, thread_id: str | None) -> str | None:
        """Refresh the thread ID for the given agency.
        If the thread ID has changed, update the cache and return the new thread ID.
        Otherwise, return None.
        """
        new_thread_id = agency.main_thread.id
        if thread_id != new_thread_id:
            await self.cache_agency(agency, agency_id, new_thread_id)
            await self.delete_agency_from_cache(agency_id, thread_id)
            return new_thread_id
        return None

    @staticmethod
    def get_cache_key(agency_id: str, thread_id: str | None) -> str:
        """Get the cache key for the given agency ID and thread ID."""
        return f"{agency_id}/{thread_id}" if thread_id else agency_id

    @staticmethod
    def load_agency_from_config(agency_id: str) -> Agency:
        """Load the agency from the config file. The agency is created using the agency-swarm library.

        This code is synchronous and should be run in a single thread.
        The code is currently not thread safe (due to agency-swarm limitations).
        """

        start = time.time()
        config = AgencyConfig.load(agency_id)

        agents = {
            agent_conf.role: Agent(
                id=agent_conf.id,
                name=f"{agent_conf.role}_{agency_id}",
                description=agent_conf.description,
                instructions=agent_conf.instructions,
                files_folder=agent_conf.files_folder,
                tools=[TOOL_MAPPING[tool] for tool in agent_conf.tools if tool in TOOL_MAPPING],
            )
            for agent_conf in config.agents
        }

        # Create agency chart based on the config
        agency_chart = [
            [agents[role] for role in chart] if isinstance(chart, list) else agents[chart]
            for chart in config.agency_chart
        ]

        # Create the agency using external library agency-swarm. It is a wrapper around OpenAI API.
        # It saves all the settings in the settings.json file (in the root folder, not thread safe)
        agency = Agency(agency_chart, shared_instructions=config.agency_manifesto)

        config.update_agent_ids_in_config(agency.agents)
        config.save()

        logger.info(f"Agency creation took {time.time() - start} seconds. Session ID: {agency_id}")
        return agency
