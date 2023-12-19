import logging

from agency_swarm import Agency
from fastapi import APIRouter, HTTPException

from nalgonda.agency_manager import AgencyManager
from nalgonda.models.request_models import AgencyMessagePostRequest

logger = logging.getLogger(__name__)
agency_router = APIRouter(
    responses={404: {"description": "Not found"}},
)
agency_manager = AgencyManager()


@agency_router.post("/agency")
async def create_agency() -> dict:
    """Create a new agency and return its id."""
    # TODO: Add authentication: check if user is logged in and has permission to create an agency

    _, agency_id = await agency_manager.create_agency()
    return {"agency_id": agency_id}


@agency_router.post("/agency/message")
async def post_agency_message(request: AgencyMessagePostRequest) -> dict:
    """Send a message to the CEO of the given agency."""
    # TODO: Add authentication: check if agency_id is valid for the given user

    user_message = request.message
    agency_id = request.agency_id
    thread_id = request.thread_id

    logger.info(f"Received message: {user_message}, agency_id: {agency_id}, thread_id: {thread_id}")

    agency = await agency_manager.get_agency(agency_id, thread_id)
    if not agency:
        raise HTTPException(status_code=404, detail="Agency not found")

    try:
        response = await process_message(user_message, agency)

        new_thread_id = await agency_manager.refresh_thread_id(agency, agency_id, thread_id)
        if new_thread_id is not None:
            logger.info(f"Thread ID changed from {thread_id} to {new_thread_id}")
            return {"response": response, "thread_id": new_thread_id}

        return {"response": response}
    except Exception as e:
        logger.exception(e)
        return {"error": str(e)}


async def process_message(user_message: str, agency: Agency) -> str:
    """Process a message from the user and return the response from the CEO."""
    response = agency.get_completion(message=user_message, yield_messages=False)
    return response
