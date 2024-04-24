import asyncio
import logging
from datetime import UTC, datetime
from http import HTTPStatus

from agency_swarm import Agent
from fastapi import HTTPException

from backend.custom_skills import SKILL_MAPPING
from backend.models.agent_flow_spec import AgentFlowSpec
from backend.models.skill_config import SkillConfig
from backend.repositories.agent_flow_spec_storage import AgentFlowSpecStorage
from backend.repositories.skill_config_storage import SkillConfigStorage
from backend.services.user_secret_manager import UserSecretManager
from backend.settings import settings

logger = logging.getLogger(__name__)


class AgentManager:
    def __init__(
        self, storage: AgentFlowSpecStorage, user_secret_manager: UserSecretManager, skill_storage: SkillConfigStorage
    ) -> None:
        self.user_secret_manager = user_secret_manager
        self.storage = storage
        self.skill_storage = skill_storage

    async def get_agent_list(self, user_id: str, owned_by_user: bool = False) -> list[AgentFlowSpec]:
        user_configs = self.storage.load_by_user_id(user_id)
        template_configs = self.storage.load_by_user_id(None) if not owned_by_user else []
        return user_configs + template_configs

    async def handle_agent_creation_or_update(self, config: AgentFlowSpec, current_user_id: str) -> str:
        """Create or update an agent. If the agent already exists, it will be updated."""
        # Support template configs
        if not config.user_id:
            logger.info(f"Creating agent for user: {current_user_id}, agent: {config.config.name}")
            config.id = None

        # Check permissions and validate agent name
        if config.id:
            config_db = self.storage.load_by_id(config.id)
            if not config_db:
                raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Agent not found")
            self._validate_agent_ownership(config_db, current_user_id)
            self._validate_agent_name(config, config_db)

        # Ensure the agent is associated with the current user
        config.user_id = current_user_id
        config.timestamp = datetime.now(UTC).isoformat()

        # Validate skills
        skills_db = self.skill_storage.load_by_titles(config.skills)
        self._validate_skills(config.skills, skills_db)

        return await self._create_or_update_agent(config)

    async def delete_agent(self, agent_id: str, current_user_id: str) -> None:
        config = self.storage.load_by_id(agent_id)
        if not config:
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Agent not found")
        self._validate_agent_ownership(config, current_user_id)
        self.storage.delete(agent_id)

    async def get_agent(self, agent_id: str) -> tuple[Agent, AgentFlowSpec] | None:
        config = self.storage.load_by_id(agent_id)
        if not config:
            logger.error(f"Agent configuration for {agent_id} could not be found in the Firestore database.")
            return None
        agent = await asyncio.to_thread(self._construct_agent, config)
        return agent, config

    async def is_agent_used_in_agency(self, agent_id: str) -> bool:
        """Check if the agent is part of any agency configurations."""
        return len(self.storage.load_by_agent_id(agent_id)) > 0

    async def _create_or_update_agent(self, config: AgentFlowSpec) -> str:
        """Create or update an agent. If the agent already exists, it will be updated."""
        # FIXME: a workaround explained at the top of the file api/agent.py
        if not config.config.name.endswith(f" ({config.user_id})"):
            config.config.name = f"{config.config.name} ({config.user_id})"

        agent = await asyncio.to_thread(self._construct_agent, config)
        await asyncio.to_thread(agent.init_oai)  # initialize the openai agent to get the id
        config.id = agent.id
        self.storage.save(config)
        return agent.id

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
        return agent

    @staticmethod
    def _validate_agent_ownership(config_db: AgentFlowSpec, current_user_id: str) -> None:
        if config_db.user_id != current_user_id:
            raise HTTPException(
                status_code=HTTPStatus.FORBIDDEN, detail="You don't have permissions to access this agent"
            )

    @staticmethod
    def _validate_agent_name(config: AgentFlowSpec, config_db: AgentFlowSpec) -> None:
        if config.config.name != config_db.config.name:
            raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail="Renaming agents is not supported yet")

    @staticmethod
    def _validate_skills(skills: list[str], skills_db: list[SkillConfig]) -> None:
        # Check if all skills are supported
        unsupported_skills = set(skills) - set(SKILL_MAPPING.keys())
        if unsupported_skills:
            raise HTTPException(
                status_code=HTTPStatus.BAD_REQUEST, detail=f"Some skills are not supported: {unsupported_skills}"
            )

        # Check if all skills are approved
        unapproved_skills = set(skills) - {skill.title for skill in skills_db if skill.approved}
        if unapproved_skills:
            raise HTTPException(
                status_code=HTTPStatus.BAD_REQUEST, detail=f"Some skills are not approved: {unapproved_skills}"
            )
