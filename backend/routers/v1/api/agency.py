import asyncio
import logging
from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi.params import Query

from backend.dependencies.auth import get_current_user
from backend.dependencies.dependencies import get_agency_manager
from backend.models.agency_config import AgencyConfig
from backend.models.auth import User
from backend.repositories.agency_config_firestore_storage import AgencyConfigFirestoreStorage
from backend.repositories.agent_flow_spec_firestore_storage import AgentFlowSpecFirestoreStorage
from backend.services.agency_manager import AgencyManager
from backend.services.env_vars_manager import ContextEnvVarsManager

logger = logging.getLogger(__name__)
agency_router = APIRouter(
    responses={404: {"description": "Not found"}},
    tags=["agency"],
)


@agency_router.get("/agency/list")
async def get_agency_list(
    current_user: Annotated[User, Depends(get_current_user)],
    storage: AgencyConfigFirestoreStorage = Depends(AgencyConfigFirestoreStorage),
) -> list[AgencyConfig]:
    agencies = storage.load_by_user_id(current_user.id) + storage.load_by_user_id(None)
    return agencies


@agency_router.get("/agency")
async def get_agency_config(
    current_user: Annotated[User, Depends(get_current_user)],
    agency_id: str = Query(..., description="The unique identifier of the agency"),
    storage: AgencyConfigFirestoreStorage = Depends(AgencyConfigFirestoreStorage),
) -> AgencyConfig:
    agency_config = storage.load_by_agency_id(agency_id)
    if not agency_config:
        logger.warning(f"Agency not found: {agency_id}, user: {current_user.id}")
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Agency not found")
    # check if the current_user has permissions to get the agency config
    if agency_config.user_id and agency_config.user_id != current_user.id:
        logger.warning(f"User {current_user.id} does not have permissions to get agency {agency_id}")
        raise HTTPException(status_code=HTTPStatus.FORBIDDEN, detail="Forbidden")
    return agency_config


@agency_router.put("/agency", status_code=HTTPStatus.OK)
async def update_or_create_agency(
    agency_config: AgencyConfig,
    current_user: Annotated[User, Depends(get_current_user)],
    agency_manager: AgencyManager = Depends(get_agency_manager),
    agency_storage: AgencyConfigFirestoreStorage = Depends(AgencyConfigFirestoreStorage),
    agent_storage: AgentFlowSpecFirestoreStorage = Depends(AgentFlowSpecFirestoreStorage),
):
    """Create or update an agency and return its id"""
    # support template configs:
    if not agency_config.user_id:
        logger.info(f"Creating agency for user: {current_user.id}, agency: {agency_config.name}")
        agency_config.agency_id = None
    else:
        # check if the current_user has permissions
        if agency_config.agency_id:
            agency_config_db = agency_storage.load_by_agency_id(agency_config.agency_id)
            if not agency_config_db:
                logger.warning(f"Agency not found: {agency_config.agency_id}, user: {current_user.id}")
                raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Agency not found")
            if agency_config_db.user_id != current_user.id:
                logger.warning(
                    f"User {current_user.id} does not have permissions to update agency {agency_config.agency_id}"
                )
                raise HTTPException(status_code=HTTPStatus.FORBIDDEN, detail="Forbidden")

    # check that all used agents belong to the current user
    for agent_id in agency_config.agents:
        agent_flow_spec = await asyncio.to_thread(agent_storage.load_by_id, agent_id)
        if not agent_flow_spec:
            logger.error(f"Agent not found: {agent_id}, user: {current_user.id}")
            raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail=f"Agent not found: {agent_id}")
        if agent_flow_spec.user_id != current_user.id:
            logger.warning(f"User {current_user.id} does not have permissions to use agent {agent_id}")
            raise HTTPException(status_code=HTTPStatus.FORBIDDEN, detail="Forbidden")
    # FIXME: current limitation: all agents must belong to the current user.
    # to fix: If the agent is a template (agent_flow_spec.user_id is None), it should be copied for the current user
    # (reuse the code from api/agent.py)

    # Ensure the agency is associated with the current user
    agency_config.user_id = current_user.id

    # Set the user_id in the context variables
    ContextEnvVarsManager.set("user_id", current_user.id)

    agency_id = await agency_manager.update_or_create_agency(agency_config)

    return {"agency_id": agency_id}
