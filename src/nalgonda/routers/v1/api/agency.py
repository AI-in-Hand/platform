import asyncio
import logging
import uuid

from agency_manager import AgencyManager
from agency_swarm import Agency
from agency_swarm.messages import MessageOutput
from fastapi import APIRouter

logger = logging.getLogger(__name__)
agency_manager = AgencyManager()

agency_api_router = APIRouter(
    responses={404: {"description": "Not found"}},
)


@agency_api_router.post("/")
async def create_agency():
    """Create a new agency and return its id."""
    # TODO: Add authentication: check if user is logged in and has permission to create an agency

    agency_id = uuid.uuid4().hex
    await agency_manager.get_or_create_agency(agency_id)
    return {"agency_id": agency_id}


@agency_api_router.post("/message")
async def send_message(agency_id: str, message: str):
    """Send a message to the CEO of the given agency."""
    # TODO: Add authentication: check if agency_id is valid for the given user

    logger.info(f"Received message: {message} for agency: {agency_id}")
    agency = await agency_manager.get_or_create_agency(agency_id=agency_id)

    try:
        await process_message(message, agency)
    except Exception as e:
        logger.exception(e)


async def process_message(user_message: str, agency: Agency) -> str:
    """Process a message from the user and return the response from the CEO."""
    loop = asyncio.get_running_loop()

    gen = agency.get_completion(message=user_message, yield_messages=False)  # False: get only the final CEO message

    def get_next() -> MessageOutput:
        return next(gen)

    response = await loop.run_in_executor(None, get_next)
    return response.get_formatted_content()
