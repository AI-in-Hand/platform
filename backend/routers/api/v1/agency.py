import logging
from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Body, Depends, HTTPException
from fastapi.params import Query

from backend.dependencies.auth import get_current_user
from backend.dependencies.dependencies import get_agency_adapter, get_agency_manager
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
    agencies = await manager.get_agency_list(current_user.id)
    agencies_for_api = [adapter.to_api(agency) for agency in agencies]
    return AgencyListResponse(data=agencies_for_api)


@agency_router.get("/agency")
async def get_agency_config(
    current_user: Annotated[User, Depends(get_current_user)],
    adapter: Annotated[AgencyAdapter, Depends(get_agency_adapter)],
    id: str = Query(..., description="The unique identifier of the agency"),
    storage: AgencyConfigStorage = Depends(AgencyConfigStorage),
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
    config_for_api = adapter.to_api(agency_config)
    return GetAgencyResponse(data=config_for_api)


@agency_router.put("/agency", status_code=HTTPStatus.OK)
async def update_or_create_agency(
    current_user: Annotated[User, Depends(get_current_user)],
    adapter: Annotated[AgencyAdapter, Depends(get_agency_adapter)],
    config: AgencyConfigForAPI = Body(...),
    manager: AgencyManager = Depends(get_agency_manager),
) -> AgencyListResponse:
    """Create or update an agency and return its id"""
    # Transform the API model to the internal model
    config = adapter.to_model(config)

    # Set the user_id in the context variables
    ContextEnvVarsManager.set("user_id", current_user.id)

    await manager.handle_agency_creation_or_update(config, current_user.id)

    agencies = await manager.get_agency_list(current_user.id)
    agencies_for_api = [adapter.to_api(agency) for agency in agencies]
    return AgencyListResponse(message="Agency updated", data=agencies_for_api)


@agency_router.delete("/agency")
async def delete_agency(
    current_user: Annotated[User, Depends(get_current_user)],
    adapter: Annotated[AgencyAdapter, Depends(get_agency_adapter)],
    id: str = Query(..., description="The unique identifier of the agency"),
    manager: AgencyManager = Depends(get_agency_manager),
    storage: AgencyConfigStorage = Depends(AgencyConfigStorage),
) -> AgencyListResponse:
    """Delete an agency"""
    db_config = storage.load_by_id(id)
    if not db_config:
        logger.warning(f"Agency not found: {id}, user: {current_user.id}")
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Agency not found")
    if db_config.user_id != current_user.id:
        logger.warning(f"User {current_user.id} does not have permissions to delete agency {id}")
        raise HTTPException(status_code=HTTPStatus.FORBIDDEN, detail="Forbidden")

    await manager.delete_agency(id)

    agencies = await manager.get_agency_list(current_user.id)
    agencies_for_api = [adapter.to_api(agency) for agency in agencies]
    return AgencyListResponse(message="Agency deleted", data=agencies_for_api)
