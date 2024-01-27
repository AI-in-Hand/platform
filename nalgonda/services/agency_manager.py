import asyncio
import logging
from copy import copy

from agency_swarm import Agency, Agent, get_openai_client

from nalgonda.models.agency_config import AgencyConfig
from nalgonda.persistence.agency_config_firestore_storage import AgencyConfigFirestoreStorage
from nalgonda.services.agent_manager import AgentManager
from nalgonda.services.caching.redis_cache_manager import RedisCacheManager

logger = logging.getLogger(__name__)


class AgencyManager:
    def __init__(
        self,
        cache_manager: RedisCacheManager,
        agent_manager: AgentManager,
        agency_config_storage: AgencyConfigFirestoreStorage,
    ) -> None:
        self.agency_config_storage = agency_config_storage
        self.cache_manager = cache_manager
        self.agent_manager = agent_manager

    async def get_agency(self, agency_id: str, thread_id: str | None = None) -> Agency | None:
        cache_key = self.get_cache_key(agency_id, thread_id)
        agency = await self.cache_manager.get(cache_key)

        if not agency:
            # If agency is not found in the cache, re-populate the cache
            agency = await self.repopulate_cache_and_update_assistants(agency_id)
            if not agency:
                logger.error(f"Agency configuration for {agency_id} could not be found in the Firestore database.")
                return None

        agency = self._restore_client_objects(agency)
        return agency

    async def update_agency(self, agency_config: AgencyConfig) -> None:
        """Update the agency. It will update the agency in the firestore and also in the cache."""
        agency_id = agency_config.agency_id

        AgencyConfig.model_validate(agency_config.model_dump())

        await asyncio.to_thread(self.agency_config_storage.save, agency_id, agency_config)

        # Update the agency in the cache
        await self.repopulate_cache_and_update_assistants(agency_id)

    async def repopulate_cache_and_update_assistants(self, agency_id: str) -> Agency | None:
        """Gets the agency config from the Firestore, constructs agents and agency
        (agency-swarm also updates assistants), and saves the Agency instance to Redis
        (with expiration period, see constants.DEFAULT_CACHE_EXPIRATION).
        """
        agency_config = await asyncio.to_thread(self.agency_config_storage.load_by_agency_id, agency_id)
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
        agency_copy = copy(agency)
        agency_copy.agents = [copy(agent) for agent in agency_copy.agents]

        for agent in agency_copy.agents:
            agent.client = None

        agency_copy.main_thread = copy(agency_copy.main_thread)
        agency_copy.main_thread.client = None

        if agency_copy.main_thread.recipient_agent:
            agency_copy.main_thread.recipient_agent = copy(agency_copy.main_thread.recipient_agent)
            agency_copy.main_thread.recipient_agent.client = None

        if agency_copy.ceo:
            agency_copy.ceo = copy(agency_copy.ceo)
            agency_copy.ceo.client = None

        return agency_copy

    @staticmethod
    def _restore_client_objects(agency: Agency) -> Agency:
        """Restore all client objects from the agency object"""
        for agent in agency.agents:
            agent.client = get_openai_client()
        agency.main_thread.client = get_openai_client()
        return agency
