import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from starlette.status import HTTP_403_FORBIDDEN, HTTP_404_NOT_FOUND

from nalgonda.dependencies.auth import get_current_active_user
from nalgonda.dependencies.dependencies import get_agency_manager, get_thread_manager
from nalgonda.models.auth import UserInDB
from nalgonda.models.request_models import ThreadPostRequest
from nalgonda.persistence.agency_config_firestore_storage import AgencyConfigFirestoreStorage
from nalgonda.services.agency_manager import AgencyManager
from nalgonda.services.thread_manager import ThreadManager

logger = logging.getLogger(__name__)
thread_router = APIRouter(
    responses={404: {"description": "Not found"}},
    tags=["thread"],
)


@thread_router.get("/thread")
async def get_threads():
    ...


@thread_router.post("/thread")
async def create_thread(
    request: ThreadPostRequest,
    current_user: Annotated[UserInDB, Depends(get_current_active_user)],
    agency_manager: AgencyManager = Depends(get_agency_manager),
    thread_manager: ThreadManager = Depends(get_thread_manager),
    storage: AgencyConfigFirestoreStorage = Depends(AgencyConfigFirestoreStorage),
) -> dict:
    """Create a new thread for the given agency and return its id."""
    agency_id = request.agency_id
    # check if the current_user has permissions to create a thread for the agency
    agency_config = storage.load_by_agency_id(agency_id)
    if not agency_config:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="Agency configuration not found")
    if agency_config.owner_id != current_user.id:
        raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail="Forbidden")

    logger.info(f"Creating a new thread for the agency: {agency_id}, and user: {current_user.id}")

    agency = await agency_manager.get_agency(agency_id, None)
    if not agency:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="Agency not found, create an agency first")

    thread_id = thread_manager.create_threads(agency)

    await agency_manager.cache_agency(agency, agency_id, thread_id)
    return {"thread_id": thread_id}
