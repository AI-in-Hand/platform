import asyncio
import logging

from agency_swarm import Agent

from nalgonda.custom_tools import TOOL_MAPPING
from nalgonda.models.agent_config import AgentConfig
from nalgonda.repositories.agent_config_firestore_storage import AgentConfigFirestoreStorage
from nalgonda.services.oai_client import get_openai_client
from nalgonda.settings import settings

logger = logging.getLogger(__name__)


class AgentManager:
    def __init__(self, storage: AgentConfigFirestoreStorage) -> None:
        self.storage = storage

    async def create_or_update_agent(self, agent_config: AgentConfig) -> str:
        """Create or update an agent. If the agent already exists, it will be updated.

        Args:
            agent_config (AgentConfig): agent configuration
        Returns:
            str: agent_id
        """

        # FIXME: a workaround explained at the top of the file api/agent.py
        if not agent_config.name.endswith(f" ({agent_config.owner_id})"):
            agent_config.name = f"{agent_config.name} ({agent_config.owner_id})"

        agent = await asyncio.to_thread(self._construct_agent, agent_config)
        await asyncio.to_thread(agent.init_oai)  # initialize the openai agent to get the id
        if not agent.id:
            logger.error(f"Agent id could not be initialized for {agent_config}.")
            raise RuntimeError("Agent id could not be initialized.")
        agent_config.agent_id = agent.id
        await asyncio.to_thread(self.storage.save, agent_config)
        return agent.id

    async def get_agent(self, agent_id: str) -> tuple[Agent, AgentConfig] | None:
        agent_config = await asyncio.to_thread(self.storage.load_by_agent_id, agent_id)
        if not agent_config:
            logger.error(f"Agent configuration for {agent_id} could not be found in the Firestore database.")
            return None

        agent = await asyncio.to_thread(self._construct_agent, agent_config)
        return agent, agent_config

    @staticmethod
    def _construct_agent(agent_config: AgentConfig) -> Agent:
        agent = Agent(
            id=agent_config.agent_id,
            name=agent_config.name,
            description=agent_config.description,
            instructions=agent_config.instructions,
            files_folder=agent_config.files_folder,
            tools=[TOOL_MAPPING[tool] for tool in agent_config.tools],
            model=settings.gpt_model,
        )
        # a workaround: agent.client must be replaced with a proper implementation
        agent.client = get_openai_client()
        return agent
