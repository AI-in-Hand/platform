import asyncio
import logging
from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi.params import Query

from backend.dependencies.auth import get_current_user
from backend.dependencies.dependencies import get_agency_config_adapter, get_agency_manager
from backend.models.agency_config import AgencyConfigForAPI
from backend.models.auth import User
from backend.models.response_models import (
    CreateAgencyData,
    CreateAgencyResponse,
    GetAgencyListResponse,
    GetAgencyResponse,
)
from backend.repositories.agency_config_firestore_storage import AgencyConfigFirestoreStorage
from backend.repositories.agent_flow_spec_firestore_storage import AgentFlowSpecFirestoreStorage
from backend.services.adapters.agency_adapter import AgencyConfigAdapter
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
    agency_adapter: Annotated[AgencyConfigAdapter, Depends(get_agency_config_adapter)],
    storage: AgencyConfigFirestoreStorage = Depends(AgencyConfigFirestoreStorage),
) -> GetAgencyListResponse:
    agencies = storage.load_by_user_id(current_user.id) + storage.load_by_user_id(None)
    agencies_for_api = [agency_adapter.to_api(agency) for agency in agencies]
    return GetAgencyListResponse(data=agencies_for_api)


@agency_router.get("/agency")
async def get_agency_config(
    current_user: Annotated[User, Depends(get_current_user)],
    agency_adapter: Annotated[AgencyConfigAdapter, Depends(get_agency_config_adapter)],
    id: str = Query(..., description="The unique identifier of the agency"),
    storage: AgencyConfigFirestoreStorage = Depends(AgencyConfigFirestoreStorage),
) -> GetAgencyResponse:
    agency_config = storage.load_by_id(id)
    if not agency_config:
        logger.warning(f"Agency not found: {id}, user: {current_user.id}")
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Agency not found")
    # check if the current_user has permissions to get the agency config
    if agency_config.user_id and agency_config.user_id != current_user.id:
        logger.warning(f"User {current_user.id} does not have permissions to get agency {id}")
        raise HTTPException(status_code=HTTPStatus.FORBIDDEN, detail="Forbidden")

    # Transform the internal model to the API model
    config_for_api = agency_adapter.to_api(agency_config)
    return GetAgencyResponse(data=config_for_api)


@agency_router.put("/agency", status_code=HTTPStatus.OK)
async def update_or_create_agency(
    agency_config: AgencyConfigForAPI,
    current_user: Annotated[User, Depends(get_current_user)],
    agency_adapter: Annotated[AgencyConfigAdapter, Depends(get_agency_config_adapter)],
    agency_manager: AgencyManager = Depends(get_agency_manager),
    agency_storage: AgencyConfigFirestoreStorage = Depends(AgencyConfigFirestoreStorage),
    agent_storage: AgentFlowSpecFirestoreStorage = Depends(AgentFlowSpecFirestoreStorage),
):
    """Create or update an agency and return its id"""
    # Transform the API model to the internal model
    agency_config = agency_adapter.to_model(agency_config)

    # support template configs:
    if not agency_config.user_id:
        logger.info(f"Creating agency for user: {current_user.id}, agency: {agency_config.name}")
        agency_config.id = None
    else:
        # check if the current_user has permissions
        if agency_config.id:
            agency_config_db = agency_storage.load_by_id(agency_config.id)
            if not agency_config_db:
                logger.warning(f"Agency not found: {agency_config.id}, user: {current_user.id}")
                raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Agency not found")
            if agency_config_db.user_id != current_user.id:
                logger.warning(f"User {current_user.id} does not have permissions to update agency {agency_config.id}")
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

    id_ = await agency_manager.update_or_create_agency(agency_config)

    return CreateAgencyResponse(data=CreateAgencyData(id=id_))
