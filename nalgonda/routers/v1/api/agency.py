import logging
from http import HTTPStatus
from typing import Annotated

from agency_swarm import Agency
from fastapi import APIRouter, Depends, HTTPException
from starlette.status import HTTP_200_OK, HTTP_404_NOT_FOUND

from nalgonda.dependencies.agency_manager import AgencyManager, get_agency_manager
from nalgonda.dependencies.auth import get_current_active_user
from nalgonda.dependencies.thread_manager import ThreadManager, get_thread_manager
from nalgonda.models.auth import User
from nalgonda.models.request_models import AgencyMessagePostRequest, AgencyThreadPostRequest
from nalgonda.persistence.agency_config_firestore_storage import AgencyConfigFirestoreStorage

logger = logging.getLogger(__name__)
agency_router = APIRouter(
    responses={404: {"description": "Not found"}},
)


@agency_router.post("/agency")
async def create_agency(
    current_user: Annotated[User, Depends(get_current_active_user)],
    agency_manager: AgencyManager = Depends(get_agency_manager),
) -> dict:
    """Create a new agency and return its id."""
    # TODO: check if the current_user has permission to create an agency
    logger.info(f"Creating agency for user: {current_user.username}")

    agency_id = await agency_manager.create_agency()
    return {"agency_id": agency_id}


@agency_router.post("/agency/thread")
async def create_agency_thread(
    request: AgencyThreadPostRequest,
    current_user: Annotated[User, Depends(get_current_active_user)],
    agency_manager: AgencyManager = Depends(get_agency_manager),
    thread_manager: ThreadManager = Depends(get_thread_manager),
) -> dict:
    """Create a new thread for the given agency and return its id."""
    agency_id = request.agency_id

    logger.info(f"Creating a new thread for the agency: {agency_id}, and user: {current_user.username}")

    agency = await agency_manager.get_agency(agency_id, None)
    if not agency:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Agency not found, create an agency first")

    thread_id = thread_manager.create_threads(agency)

    await agency_manager.cache_agency(agency, agency_id, thread_id)
    return {"thread_id": thread_id}


@agency_router.get("/agency/config")
async def get_agency_config(agency_id: str):
    storage = AgencyConfigFirestoreStorage(agency_id)
    agency_config = storage.load()
    if not agency_config:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="Agency configuration not found")
    return agency_config


@agency_router.put("/agency/config", status_code=HTTP_200_OK)
async def update_agency_config(
    agency_id: str,
    updated_data: dict,
    current_user: Annotated[User, Depends(get_current_active_user)],
    agency_manager: AgencyManager = Depends(get_agency_manager),
):
    storage = AgencyConfigFirestoreStorage(agency_id)
    agency_config = storage.load()
    if not agency_config:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="Agency configuration not found")

    updated_data["owner_id"] = current_user.username
    await agency_manager.update_agency(agency_config, updated_data)

    return {"message": "Agency configuration updated successfully"}


@agency_router.post("/agency/message")
async def post_agency_message(
    request: AgencyMessagePostRequest, agency_manager: AgencyManager = Depends(get_agency_manager)
) -> dict:
    """Send a message to the CEO of the given agency."""
    # TODO: Add authentication: check if agency_id is valid for the given user

    user_message = request.message
    agency_id = request.agency_id
    thread_id = request.thread_id

    logger.info(f"Received message: {user_message}, agency_id: {agency_id}, thread_id: {thread_id}")

    agency = await agency_manager.get_agency(agency_id, thread_id)
    if not agency:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Agency not found, create an agency first")

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
