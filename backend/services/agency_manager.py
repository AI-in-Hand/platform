import logging
from datetime import UTC, datetime
from http import HTTPStatus
from typing import Any

from agency_swarm import Agency, Agent
from fastapi import HTTPException

from backend.exceptions import NotFoundError
from backend.models.agency_config import AgencyConfig
from backend.repositories.agency_config_storage import AgencyConfigStorage
from backend.services.agent_manager import AgentManager
from backend.services.user_variable_manager import UserVariableManager

logger = logging.getLogger(__name__)


class AgencyManager:
    def __init__(
        self,
        agent_manager: AgentManager,
        agency_config_storage: AgencyConfigStorage,
        user_variable_manager: UserVariableManager,
    ) -> None:
        self.storage = agency_config_storage
        self.agent_manager = agent_manager
        self.user_variable_manager = user_variable_manager

    async def get_agency_list(self, user_id: str) -> list[AgencyConfig]:
        """Get the list of agencies for the user. It will return the agencies for the user and the templates."""
        user_agencies = self.storage.load_by_user_id(user_id)
        template_agencies = self.storage.load_by_user_id(None)
        agencies = user_agencies + template_agencies
        sorted_agencies = sorted(agencies, key=lambda x: x.timestamp, reverse=True)
        return sorted_agencies

    async def get_agency(
        self, id_: str, thread_ids: dict[str, Any], user_id: str, allow_template: bool = False
    ) -> tuple[Agency, AgencyConfig]:
        """Get the agency from the Firestore. It will construct the agency and update the assistants."""
        agency_config = self.storage.load_by_id(id_)
        if not agency_config:
            raise NotFoundError("Agency", id_)

        self.validate_agency_ownership(agency_config.user_id, user_id, allow_template=allow_template)

        agency = await self._construct_agency_and_update_assistants(agency_config, thread_ids)
        return agency, agency_config

    def is_agent_used_in_agencies(self, agent_id: str) -> bool:
        """Check if the agent is part of any agency configurations."""
        return len(self.storage.load_by_agent_id(agent_id)) > 0

    async def handle_agency_creation_or_update(self, config: AgencyConfig, current_user_id: str) -> str:
        """Handle the agency creation or update. It will check the permissions and update the agency in the Firestore
        and the cache. It will also update the assistants.
        """
        # support template configs:
        if not config.user_id:
            logger.info(f"Creating agency for user: {current_user_id}, agency: {config.name}")
            config.id = None  # type: ignore

        # Check permissions
        if config.id:
            config_db = self.storage.load_by_id(config.id)
            if not config_db:
                raise NotFoundError("Agency", config.id)
            self.validate_agency_ownership(config_db.user_id, current_user_id)
        self._validate_agent_ownership(config.agents, current_user_id)

        # Ensure the agency is associated with the current user
        config.user_id = current_user_id
        config.timestamp = datetime.now(UTC).isoformat()

        return await self._create_or_update_agency(config)

    async def _load_and_construct_agents(self, agency_config: AgencyConfig) -> dict[str, Agent]:
        agents = {}
        for agent_id in agency_config.agents:
            get_result = await self.agent_manager.get_agent(agent_id)
            if get_result:
                agent, agent_flow_spec = get_result
                agents[agent_flow_spec.config.name] = agent
            else:
                logger.error(f"Agent with id {agent_id} not found.")
                # TODO: Handle this error (raise exception?)
        return agents

    async def delete_agency(self, agency_id: str) -> None:
        """Delete the agency from the Firestore."""
        self.storage.delete(agency_id)

    @staticmethod
    def validate_agency_ownership(
        target_user_id: str | None, current_user_id: str, allow_template: bool = False
    ) -> None:
        """Validate the agency ownership. It will check if the current user has permissions to update the agency."""
        if not target_user_id and allow_template:
            return
        if target_user_id != current_user_id:
            raise HTTPException(
                status_code=HTTPStatus.FORBIDDEN, detail="You don't have permissions to access this agency"
            )

    async def _create_or_update_agency(self, agency_config: AgencyConfig) -> str:
        """Update or create the agency. It will update the agency in the Firestore."""
        AgencyConfig.model_validate(agency_config.model_dump())
        return self.storage.save(agency_config)

    async def _construct_agency_and_update_assistants(
        self, agency_config: AgencyConfig, thread_ids: dict[str, Any]
    ) -> Agency:
        """Create the agency using external library agency-swarm. It is a wrapper around OpenAI API.
        It saves all the settings in the settings.json file (in the root folder, not thread safe)
        Gets the agency config from the Firestore, constructs agents and agency
        (agency-swarm also updates assistants). Returns the Agency instance if successful, otherwise None.
        """
        agents = await self._load_and_construct_agents(agency_config)

        agency_chart = []
        if agents and agency_config.main_agent:
            main_agent = agents[agency_config.main_agent]
            agency_chart = [main_agent]
            if agency_config.agency_chart:
                new_agency_chart = [[agents[name] for name in layer] for layer in agency_config.agency_chart.values()]
                agency_chart.extend(new_agency_chart)

        # call Agency.__init__ to create or update the agency
        return Agency(
            agency_chart,
            shared_instructions=agency_config.shared_instructions,
            threads_callbacks=(
                {"load": lambda: thread_ids, "save": lambda x: thread_ids.update(x)} if thread_ids is not None else None
            ),
        )

    def _validate_agent_ownership(self, agents: list[str], current_user_id: str) -> None:
        """Validate the agent ownership. It will check if the current user has permissions to use the agents."""
        # check that all used agents belong to the current user
        for agent_id in agents:
            agent_flow_spec = self.agent_manager.storage.load_by_id(agent_id)
            if not agent_flow_spec:
                raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail=f"Agent not found: {agent_id}")
            if agent_flow_spec.user_id != current_user_id:
                raise HTTPException(
                    status_code=HTTPStatus.FORBIDDEN, detail=f"You don't have permissions to use agent {agent_id}"
                )
        # FIXME: current limitation: all agents must belong to the current user.
        # to fix: If the agent is a template (agent_flow_spec.user_id is None), it should be copied for the current user
        # (reuse the code from api/agent.py)
