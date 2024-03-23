import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from starlette.status import HTTP_403_FORBIDDEN, HTTP_404_NOT_FOUND

from nalgonda.dependencies.auth import get_current_user
from nalgonda.dependencies.dependencies import get_agency_manager, get_session_manager
from nalgonda.models.auth import User
from nalgonda.models.request_models import SessionPostRequest
from nalgonda.repositories.agency_config_firestore_storage import AgencyConfigFirestoreStorage
from nalgonda.repositories.session_firestore_storage import SessionConfigFirestoreStorage
from nalgonda.services.agency_manager import AgencyManager
from nalgonda.services.env_vars_manager import ContextEnvVarsManager
from nalgonda.services.session_manager import SessionManager

logger = logging.getLogger(__name__)
session_router = APIRouter(
    responses={404: {"description": "Not found"}},
    tags=["session"],
)


@session_router.get("/session/list")
async def get_session_list(
    current_user: Annotated[User, Depends(get_current_user)],
    storage: SessionConfigFirestoreStorage = Depends(SessionConfigFirestoreStorage),
):
    """Return a list of all sessions for the current user."""
    session_configs = storage.load_by_owner_id(current_user.id)
    return session_configs


@session_router.post("/session")
async def create_session(
    request: SessionPostRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    agency_manager: AgencyManager = Depends(get_agency_manager),
    agency_storage: AgencyConfigFirestoreStorage = Depends(AgencyConfigFirestoreStorage),
    session_manager: SessionManager = Depends(get_session_manager),
) -> dict:
    """Create a new session for the given agency and return its id."""
    agency_id = request.agency_id
    # check if the current_user has permissions to create a session for the agency
    agency_config_db = agency_storage.load_by_agency_id(agency_id)
    if not agency_config_db:
        logger.warning(f"Agency not found: {agency_id}, user: {current_user.id}")
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="Agency not found")
    if agency_config_db.owner_id != current_user.id:
        logger.warning(
            f"User {current_user.id} does not have permissions to create a session for the agency: {agency_id}"
        )
        raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail="Forbidden")

    # Set the owner_id in the context variables
    ContextEnvVarsManager.set("owner_id", current_user.id)

    logger.info(f"Creating a new session for the agency: {agency_id}, and user: {current_user.id}")

    agency = await agency_manager.get_agency(agency_id, None)
    if not agency:
        logger.warning(f"Agency not found: {agency_id}, user: {current_user.id}")
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="Agency not found")

    session_id = session_manager.create_session(agency, agency_id=agency_id, owner_id=current_user.id)

    await agency_manager.cache_agency(agency, agency_id, session_id)
    return {"session_id": session_id}
