import logging
from typing import Annotated

from agency_swarm import Agency
from fastapi import APIRouter, Depends, HTTPException
from starlette.status import HTTP_403_FORBIDDEN, HTTP_404_NOT_FOUND

from nalgonda.dependencies.auth import get_current_active_user
from nalgonda.dependencies.dependencies import get_agency_manager
from nalgonda.models.auth import UserInDB
from nalgonda.models.request_models import AgencyMessagePostRequest
from nalgonda.persistence.agency_config_firestore_storage import AgencyConfigFirestoreStorage
from nalgonda.services.agency_manager import AgencyManager

logger = logging.getLogger(__name__)
message_router = APIRouter(
    responses={404: {"description": "Not found"}},
    tags=["message"],
)


@message_router.post("/agency/message")
async def post_agency_message(
    current_user: Annotated[UserInDB, Depends(get_current_active_user)],
    request: AgencyMessagePostRequest,
    agency_manager: AgencyManager = Depends(get_agency_manager),
    storage: AgencyConfigFirestoreStorage = Depends(AgencyConfigFirestoreStorage),
) -> dict:
    """Send a message to the User Proxy of the given agency."""
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
    """Process a message from the user and return the response from the User Proxy."""
    response = agency.get_completion(message=user_message, yield_messages=False)
    return response
