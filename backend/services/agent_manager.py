import asyncio
import logging

from agency_swarm import Agent

from backend.custom_skills import SKILL_MAPPING
from backend.models.agent_flow_spec import AgentFlowSpec
from backend.repositories.agent_flow_spec_firestore_storage import AgentFlowSpecFirestoreStorage
from backend.services.env_config_manager import EnvConfigManager
from backend.services.oai_client import get_openai_client
from backend.settings import settings

logger = logging.getLogger(__name__)


class AgentManager:
    def __init__(self, storage: AgentFlowSpecFirestoreStorage, env_config_manager: EnvConfigManager) -> None:
        self.env_config_manager = env_config_manager
        self.storage = storage

    async def create_or_update_agent(self, config: AgentFlowSpec) -> str:
        """Create or update an agent. If the agent already exists, it will be updated."""

        # FIXME: a workaround explained at the top of the file api/agent.py
        if not config.name.endswith(f" ({config.user_id})"):
            config.name = f"{config.name} ({config.user_id})"

        agent = await asyncio.to_thread(self._construct_agent, config)
        await asyncio.to_thread(agent.init_oai)  # initialize the openai agent to get the id
        if not agent.id:
            logger.error(f"Agent id could not be initialized for {config}.")
            raise RuntimeError("Agent id could not be initialized.")
        config.id = agent.id
        await asyncio.to_thread(self.storage.save, config)
        return agent.id

    async def get_agent(self, agent_id: str) -> tuple[Agent, AgentFlowSpec] | None:
        config = await asyncio.to_thread(self.storage.load_by_id, agent_id)
        if not config:
            logger.error(f"Agent configuration for {agent_id} could not be found in the Firestore database.")
            return None

        agent = await asyncio.to_thread(self._construct_agent, config)
        return agent, config

    def _construct_agent(self, agent_config: AgentFlowSpec) -> Agent:
        agent = Agent(
            id=agent_config.id,
            name=agent_config.name,
            description=agent_config.description,
            instructions=agent_config.instructions,
            files_folder=agent_config.files_folder,
            tools=[SKILL_MAPPING[skill] for skill in agent_config.skills],
            model=settings.gpt_model,
        )
        # a workaround: agent.client must be replaced with a proper implementation
        agent.client = get_openai_client(env_config_manager=self.env_config_manager)
        return agent
