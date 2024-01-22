import logging
from typing import Annotated

from agency_swarm import Agency
from fastapi import APIRouter, Depends, HTTPException
from fastapi.params import Query
from starlette.status import HTTP_200_OK, HTTP_403_FORBIDDEN, HTTP_404_NOT_FOUND

from nalgonda.dependencies.auth import get_current_active_user
from nalgonda.dependencies.dependencies import get_agency_manager, get_thread_manager
from nalgonda.models.agency_config import AgencyConfig
from nalgonda.models.auth import UserInDB
from nalgonda.models.request_models import AgencyMessagePostRequest, AgencyThreadPostRequest
from nalgonda.persistence.agency_config_firestore_storage import AgencyConfigFirestoreStorage
from nalgonda.services.agency_manager import AgencyManager
from nalgonda.services.thread_manager import ThreadManager

logger = logging.getLogger(__name__)
agency_router = APIRouter(
    responses={404: {"description": "Not found"}},
    tags=["agency"],
)


@agency_router.get("/agency")
async def get_agency_list(
    current_user: Annotated[UserInDB, Depends(get_current_active_user)],
    storage: AgencyConfigFirestoreStorage = Depends(AgencyConfigFirestoreStorage),
) -> list[AgencyConfig]:
    agencies = storage.load_by_user_id(current_user.id)
    return agencies


@agency_router.get("/agency/config")
async def get_agency_config(
    current_user: Annotated[UserInDB, Depends(get_current_active_user)],
    agency_id: str = Query(..., description="The unique identifier of the agency"),
    storage: AgencyConfigFirestoreStorage = Depends(AgencyConfigFirestoreStorage),
) -> AgencyConfig:
    agency_config = storage.load_by_agency_id(agency_id)
    if not agency_config:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="Agency configuration not found")
    # check if the current_user has permissions to get the agency config
    if agency_config.owner_id != current_user.id:
        raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail="Forbidden")
    return agency_config


@agency_router.post("/agency")
async def create_agency(
    current_user: Annotated[UserInDB, Depends(get_current_active_user)],
    agency_manager: AgencyManager = Depends(get_agency_manager),
) -> dict:
    """Create a new agency and return its id."""
    # TODO: check if the current_user has permissions to create an agency
    logger.info(f"Creating agency for user: {current_user.id}")

    agency_id = await agency_manager.create_agency(owner_id=current_user.id)
    return {"agency_id": agency_id}


@agency_router.post("/agency/thread")
async def create_agency_thread(
    request: AgencyThreadPostRequest,
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


@agency_router.put("/agency/config", status_code=HTTP_200_OK)
async def update_agency_config(
    agency_id: str,
    updated_data: dict,
    current_user: Annotated[UserInDB, Depends(get_current_active_user)],
    agency_manager: AgencyManager = Depends(get_agency_manager),
    storage: AgencyConfigFirestoreStorage = Depends(AgencyConfigFirestoreStorage),
):
    # check if the current_user has permissions to update the agency config
    agency_config = storage.load_by_agency_id(agency_id)
    if not agency_config:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="Agency configuration not found")
    if agency_config.owner_id != current_user.id:
        raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail="Forbidden")

    updated_data.pop("owner_id", None)
    await agency_manager.update_agency(agency_config, updated_data)

    return {"message": "Agency configuration updated successfully"}


@agency_router.post("/agency/message")
async def post_agency_message(
    current_user: Annotated[UserInDB, Depends(get_current_active_user)],
    request: AgencyMessagePostRequest,
    agency_manager: AgencyManager = Depends(get_agency_manager),
    storage: AgencyConfigFirestoreStorage = Depends(AgencyConfigFirestoreStorage),
) -> dict:
    """Send a message to the CEO of the given agency."""
    # check if the current_user has permissions to send a message to the agency
    agency_config = storage.load_by_agency_id(request.agency_id)
    if not agency_config:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="Agency configuration not found")
    if agency_config.owner_id != current_user.id:
        raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail="Forbidden")

    user_message = request.message
    agency_id = request.agency_id
    thread_id = request.thread_id

    logger.info(f"Received message: {user_message}, agency_id: {agency_id}, thread_id: {thread_id}")

    agency = await agency_manager.get_agency(agency_id, thread_id)
    if not agency:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="Agency not found, create an agency first")

    try:
        response = await process_message(user_message, agency)
        return {"response": response}
    except Exception as e:
        logger.exception(e)
        return {"error": str(e)}


async def process_message(user_message: str, agency: Agency) -> str:
    """Process a message from the user and return the response from the CEO."""
    response = agency.get_completion(message=user_message, yield_messages=False)
    return response
