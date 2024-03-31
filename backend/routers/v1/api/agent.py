import logging
from datetime import UTC, datetime
from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Body, Depends, HTTPException
from fastapi.params import Query

from backend.dependencies.auth import get_current_user
from backend.dependencies.dependencies import get_agent_flow_spec_adapter, get_agent_manager
from backend.models.agent_flow_spec import AgentFlowSpecForAPI
from backend.models.auth import User
from backend.models.response_models import CreateAgentData, CreateAgentResponse, GetAgentListResponse, GetAgentResponse
from backend.repositories.agent_flow_spec_firestore_storage import AgentFlowSpecFirestoreStorage
from backend.services.adapters.agent_flow_spec_adapter import AgentFlowSpecAdapter
from backend.services.agent_manager import AgentManager
from backend.services.env_vars_manager import ContextEnvVarsManager

logger = logging.getLogger(__name__)
agent_router = APIRouter(tags=["agent"])


# FIXME: agent name should be unique (agency-swarm gets it by name from settings.json).
# The current workaround: we append the user_id to the agent name to make it unique.
# Renaming is not supported yet.


@agent_router.get("/agent/list")
async def get_agent_list(
    current_user: Annotated[User, Depends(get_current_user)],
    agent_flow_spec_adapter: Annotated[AgentFlowSpecAdapter, Depends(get_agent_flow_spec_adapter)],
    storage: AgentFlowSpecFirestoreStorage = Depends(AgentFlowSpecFirestoreStorage),
) -> GetAgentListResponse:
    configs = storage.load_by_user_id(current_user.id) + storage.load_by_user_id(None)
    configs_for_api = [agent_flow_spec_adapter.to_api(config) for config in configs]
    return GetAgentListResponse(data=configs_for_api)


@agent_router.get("/agent")
async def get_agent_config(
    current_user: Annotated[User, Depends(get_current_user)],
    agent_flow_spec_adapter: Annotated[AgentFlowSpecAdapter, Depends(get_agent_flow_spec_adapter)],
    id: str = Query(..., description="The unique identifier of the agent"),
    storage: AgentFlowSpecFirestoreStorage = Depends(AgentFlowSpecFirestoreStorage),
) -> GetAgentResponse:
    config = storage.load_by_id(id)
    if not config:
        logger.warning(f"Agent not found: {id}, user: {current_user.id}")
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Agent not found")
    # check if the current user is the owner of the agent
    if config.user_id and config.user_id != current_user.id:
        logger.warning(f"User {current_user.id} does not have permissions to access agent: {id}")
        raise HTTPException(status_code=HTTPStatus.FORBIDDEN, detail="Forbidden")
    config_for_api = agent_flow_spec_adapter.to_api(config)
    return GetAgentResponse(data=config_for_api)


@agent_router.put("/agent")
async def create_or_update_agent(
    current_user: Annotated[User, Depends(get_current_user)],
    agent_flow_spec_adapter: Annotated[AgentFlowSpecAdapter, Depends(get_agent_flow_spec_adapter)],
    config: AgentFlowSpecForAPI = Body(...),
    agent_manager: AgentManager = Depends(get_agent_manager),
    storage: AgentFlowSpecFirestoreStorage = Depends(AgentFlowSpecFirestoreStorage),
) -> CreateAgentResponse:
    config = agent_flow_spec_adapter.to_model(config)
    # support template configs:
    if not config.user_id:
        logger.info(f"Creating agent for user: {current_user.id}, agent: {config.config.name}")
        config.id = None
    else:
        # check if the current_user has permissions
        if config.id:
            config_db = storage.load_by_id(config.id)
            if not config_db:
                logger.warning(f"Agent not found: {config.id}, user: {current_user.id}")
                raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Agent not found")
            if config_db.user_id != current_user.id:
                logger.warning(f"User {current_user.id} does not have permissions to access agent: {config.id}")
                raise HTTPException(status_code=HTTPStatus.FORBIDDEN, detail="Forbidden")
            # Ensure the agent name has not been changed
            if config.config.name != config_db.config.name:
                logger.warning(f"Renaming agents is not supported yet: {config.id}, user: {current_user.id}")
                raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail="Renaming agents is not supported yet")

    # Ensure the agent is associated with the current user
    config.user_id = current_user.id

    config.timestamp = datetime.now(UTC).isoformat()

    # Set the user_id in the context variables
    ContextEnvVarsManager.set("user_id", current_user.id)

    agent_id = await agent_manager.create_or_update_agent(config)
    return CreateAgentResponse(data=CreateAgentData(id=agent_id))
