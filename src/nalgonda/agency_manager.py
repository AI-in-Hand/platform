import asyncio
import logging
import time

from agency_swarm import Agency, Agent

from nalgonda.config import AgencyConfig
from nalgonda.custom_tools import TOOL_MAPPING
from nalgonda.utils.exceptions import AgencyNotFound

logger = logging.getLogger(__name__)


class AgencyManager:
    def __init__(self):
        self.cache = {}  # agency_id+thread_id: agency
        self.lock = asyncio.Lock()

    async def create_agency(self, agency_id: str) -> Agency:
        """Create the agency for the given agency ID."""
        async with self.lock:
            # Note: Async-to-Sync Bridge
            agency = await asyncio.to_thread(self.load_agency_from_config, agency_id)
            self.cache[agency_id] = agency
            return agency

    async def get_agency(self, agency_id: str, thread_id: str | None) -> Agency:
        """Get the agency for the given agency ID and thread ID."""
        async with self.lock:
            if (cache_key := self.get_cache_key(agency_id, thread_id)) in self.cache:
                return self.cache[cache_key]
            else:
                raise AgencyNotFound(f"Agency not found for agency_id/thread_id: {cache_key}")

    async def cache_agency(self, agency: Agency, agency_id: str, thread_id: str | None):
        """Cache the agency for the given agency ID and thread ID."""
        async with self.lock:
            cache_key = self.get_cache_key(agency_id, thread_id)
            self.cache[cache_key] = agency

    async def delete_agency_from_cache(self, agency_id: str, thread_id: str | None):
        async with self.lock:
            cache_key = self.get_cache_key(agency_id, thread_id)
            if cache_key in self.cache:
                del self.cache[cache_key]

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

        config.update_agent_ids_in_config(agency_id, agents=agency.agents)
        config.save(agency_id)

        logger.info(f"Agency creation took {time.time() - start} seconds. Session ID: {agency_id}")
        return agency
