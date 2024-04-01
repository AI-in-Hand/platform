import asyncio
import logging
from http import HTTPStatus

from agency_swarm import Agent
from fastapi import HTTPException

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
        if not config.config.name.endswith(f" ({config.user_id})"):
            config.config.name = f"{config.config.name} ({config.user_id})"

        agent = await asyncio.to_thread(self._construct_agent, config)
        await asyncio.to_thread(agent.init_oai)  # initialize the openai agent to get the id
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

    @staticmethod
    def validate_skills(skills: list[str]) -> None:
        if unsupported_skills := set(skills) - set(SKILL_MAPPING.keys()):
            logger.warning(f"Some skills are not supported: {unsupported_skills}")
            raise HTTPException(
                status_code=HTTPStatus.BAD_REQUEST, detail=f"Some skills are not supported: {unsupported_skills}"
            )

    def _construct_agent(self, agent_flow_spec: AgentFlowSpec) -> Agent:
        agent = Agent(
            id=agent_flow_spec.id,
            name=agent_flow_spec.config.name,
            description=agent_flow_spec.description,
            instructions=agent_flow_spec.config.system_message,
            files_folder=agent_flow_spec.config.code_execution_config.work_dir,
            tools=[SKILL_MAPPING[skill] for skill in agent_flow_spec.skills],
            model=settings.gpt_model,
        )
        # a workaround: agent.client must be replaced with a proper implementation
        agent.client = get_openai_client(env_config_manager=self.env_config_manager)
        return agent
