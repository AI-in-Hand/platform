import logging
from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Body, Depends, HTTPException
from fastapi.params import Query

from backend.dependencies.auth import get_current_user
from backend.dependencies.dependencies import get_agency_adapter, get_agency_manager, get_session_manager
from backend.models.agency_config import AgencyConfigForAPI
from backend.models.auth import User
from backend.models.response_models import (
    AgencyListResponse,
    GetAgencyResponse,
)
from backend.repositories.agency_config_storage import AgencyConfigStorage
from backend.services.adapters.agency_adapter import AgencyAdapter
from backend.services.agency_manager import AgencyManager
from backend.services.context_vars_manager import ContextEnvVarsManager
from backend.services.session_manager import SessionManager

logger = logging.getLogger(__name__)

agency_router = APIRouter(
    responses={404: {"description": "Not found"}},
    tags=["agency"],
)


@agency_router.get("/agency/list")
async def get_agency_list(
    current_user: Annotated[User, Depends(get_current_user)],
    adapter: Annotated[AgencyAdapter, Depends(get_agency_adapter)],
    manager: AgencyManager = Depends(get_agency_manager),
) -> AgencyListResponse:
    """Get the list of agencies"""
    agencies = await manager.get_agency_list(current_user.id)
    agencies_for_api = [adapter.to_api(agency) for agency in agencies]
    return AgencyListResponse(data=agencies_for_api)


@agency_router.get("/agency")
async def get_agency_config(
    current_user: Annotated[User, Depends(get_current_user)],
    adapter: Annotated[AgencyAdapter, Depends(get_agency_adapter)],
    id: str = Query(..., description="The unique identifier of the agency"),
    manager: AgencyManager = Depends(get_agency_manager),
    storage: AgencyConfigStorage = Depends(AgencyConfigStorage),
) -> GetAgencyResponse:
    """Get the agency configuration.
    NOTE: currently this endpoint is not used in the frontend.
    """
    agency_config = storage.load_by_id(id)
    if not agency_config:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Agency not found")
    manager.validate_agency_ownership(agency_config.user_id, current_user.id, allow_template=True)

    # Transform the internal model to the API model
    config_for_api = adapter.to_api(agency_config)
    return GetAgencyResponse(data=config_for_api)


@agency_router.put("/agency", status_code=HTTPStatus.OK)
async def create_or_update_agency(
    current_user: Annotated[User, Depends(get_current_user)],
    adapter: Annotated[AgencyAdapter, Depends(get_agency_adapter)],
    config: AgencyConfigForAPI = Body(...),
    manager: AgencyManager = Depends(get_agency_manager),
) -> AgencyListResponse:
    """Create or update an agency and return the list of agencies"""
    # Transform the API model to the internal model
    config = adapter.to_model(config)

    # Set the user_id in the context variables
    ContextEnvVarsManager.set("user_id", current_user.id)

    await manager.handle_agency_creation_or_update(config, current_user.id)

    agencies = await manager.get_agency_list(current_user.id)
    agencies_for_api = [adapter.to_api(agency) for agency in agencies]
    return AgencyListResponse(message="Saved", data=agencies_for_api)


@agency_router.delete("/agency")
async def delete_agency(
    current_user: Annotated[User, Depends(get_current_user)],
    adapter: Annotated[AgencyAdapter, Depends(get_agency_adapter)],
    id: str = Query(..., description="The unique identifier of the agency"),
    manager: AgencyManager = Depends(get_agency_manager),
    session_manager: SessionManager = Depends(get_session_manager),
    storage: AgencyConfigStorage = Depends(AgencyConfigStorage),
) -> AgencyListResponse:
    """Delete an agency"""
    db_config = storage.load_by_id(id)
    if not db_config:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Agency not found")
    if db_config.user_id != current_user.id:
        raise HTTPException(status_code=HTTPStatus.FORBIDDEN, detail="You don't have permissions to access this agency")

    await manager.delete_agency(id)
    session_manager.delete_sessions_by_agency_id(id)

    agencies = await manager.get_agency_list(current_user.id)
    agencies_for_api = [adapter.to_api(agency) for agency in agencies]
    return AgencyListResponse(message="Agency deleted", data=agencies_for_api)
