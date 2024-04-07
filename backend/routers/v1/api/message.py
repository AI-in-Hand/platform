import asyncio
import logging
from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from backend.dependencies.auth import get_current_user
from backend.dependencies.dependencies import get_agency_manager, get_user_secret_manager
from backend.models.auth import User
from backend.models.request_models import SessionMessagePostRequest
from backend.repositories.agency_config_storage import AgencyConfigStorage
from backend.repositories.session_storage import SessionConfigStorage
from backend.services.agency_manager import AgencyManager
from backend.services.context_vars_manager import ContextEnvVarsManager
from backend.services.oai_client import get_openai_client
from backend.services.user_secret_manager import UserSecretManager

logger = logging.getLogger(__name__)
message_router = APIRouter(
    responses={404: {"description": "Not found"}},
    tags=["message"],
)


@message_router.get("/message/list")
async def get_message_list(
    current_user: Annotated[User, Depends(get_current_user)],
    session_id: str,
    before: str | None = None,
    session_storage: SessionConfigStorage = Depends(SessionConfigStorage),
    user_secret_manager: UserSecretManager = Depends(get_user_secret_manager),
):
    """Return a list of last 20 messages for the given session."""
    # check if the current_user has permissions to send a message to the agency
    session_config = session_storage.load_by_session_id(session_id)
    if not session_config:
        logger.warning(f"Session not found: {session_id}, requested by user: {current_user.id}")
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Session not found")
    if session_config.user_id != current_user.id:
        logger.warning(f"User {current_user.id} does not have permissions to access session {session_id}")
        raise HTTPException(status_code=HTTPStatus.FORBIDDEN, detail="Forbidden")

    # Set the user_id in the context variables
    ContextEnvVarsManager.set("user_id", current_user.id)

    # use OpenAI's Assistants API to get the messages by thread_id=session_id
    client = get_openai_client(user_secret_manager)
    messages = client.beta.threads.messages.list(thread_id=session_id, limit=20, before=before)
    return messages


@message_router.post("/message")
async def post_message(
    current_user: Annotated[User, Depends(get_current_user)],
    request: SessionMessagePostRequest,
    agency_manager: AgencyManager = Depends(get_agency_manager),
    storage: AgencyConfigStorage = Depends(AgencyConfigStorage),
) -> dict:
    """Send a message to the User Proxy of the given agency."""
    agency_id = request.agency_id
    user_id = current_user.id
    user_message = request.message
    session_id = request.session_id

    # check if the current_user has permissions to send a message to the agency
    agency_config = storage.load_by_id(agency_id)
    if not agency_config:
        logger.warning(f"Agency not found: {agency_id}, requested by user: {user_id}")
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Agency not found")
    if agency_config.user_id != user_id:
        logger.warning(f"User {user_id} does not have permissions to access agency {agency_id}")
        raise HTTPException(status_code=HTTPStatus.FORBIDDEN, detail="Forbidden")

    # Set the user_id and agency_id in the context variables
    ContextEnvVarsManager.set("user_id", user_id)
    ContextEnvVarsManager.set("agency_id", agency_id)

    logger.info(f"Received message: {user_message}, agency_id: {agency_id}, session_id: {session_id}")

    agency = await agency_manager.get_agency(agency_id, session_id)
    if not agency:
        logger.warning(f"Agency not found: {agency_id}, requested by user: {user_id}")
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Agency not found")

    try:
        response = await asyncio.to_thread(
            agency.get_completion, message=user_message, yield_messages=False, message_files=None
        )
        return {"response": response}
    except Exception as e:
        logger.exception(f"Error sending message to agency {agency_id}, session {session_id}")
        raise HTTPException(status_code=500, detail="Something went wrong") from e
