import asyncio
import logging
from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from nalgonda.dependencies.auth import get_current_user
from nalgonda.dependencies.dependencies import get_agency_manager
from nalgonda.models.auth import User
from nalgonda.models.request_models import SessionMessagePostRequest
from nalgonda.repositories.agency_config_firestore_storage import AgencyConfigFirestoreStorage
from nalgonda.repositories.env_config_firestore_storage import EnvConfigFirestoreStorage
from nalgonda.repositories.session_firestore_storage import SessionConfigFirestoreStorage
from nalgonda.services.agency_manager import AgencyManager
from nalgonda.services.env_vars_manager import ContextEnvVarsManager
from nalgonda.services.oai_client import get_openai_client

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
    session_storage: SessionConfigFirestoreStorage = Depends(SessionConfigFirestoreStorage),
    env_config_storage: EnvConfigFirestoreStorage = Depends(EnvConfigFirestoreStorage),
):
    """Return a list of last 20 messages for the given session."""
    # check if the current_user has permissions to send a message to the agency
    session_config = session_storage.load_by_session_id(session_id)
    if not session_config:
        logger.warning(f"Session not found: {session_id}, requested by user: {current_user.id}")
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Session not found")
    if session_config.owner_id != current_user.id:
        logger.warning(f"User {current_user.id} does not have permissions to access session {session_id}")
        raise HTTPException(status_code=HTTPStatus.FORBIDDEN, detail="Forbidden")

    # Set the owner_id in the context variables
    ContextEnvVarsManager.set("owner_id", current_user.id)

    # use OpenAI's Assistants API to get the messages by thread_id=session_id
    client = get_openai_client(env_config_storage)
    messages = client.beta.threads.messages.list(thread_id=session_id, limit=20, before=before)
    return messages


@message_router.post("/message")
async def post_message(
    current_user: Annotated[User, Depends(get_current_user)],
    request: SessionMessagePostRequest,
    agency_manager: AgencyManager = Depends(get_agency_manager),
    storage: AgencyConfigFirestoreStorage = Depends(AgencyConfigFirestoreStorage),
) -> dict:
    """Send a message to the User Proxy of the given agency."""
    agency_id = request.agency_id
    user_id = current_user.id
    user_message = request.message
    session_id = request.session_id

    # check if the current_user has permissions to send a message to the agency
    agency_config = storage.load_by_agency_id(agency_id)
    if not agency_config:
        logger.warning(f"Agency not found: {agency_id}, requested by user: {user_id}")
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Agency not found")
    if agency_config.owner_id != user_id:
        logger.warning(f"User {user_id} does not have permissions to access agency {agency_id}")
        raise HTTPException(status_code=HTTPStatus.FORBIDDEN, detail="Forbidden")

    # Set the owner_id and agency_id in the context variables
    ContextEnvVarsManager.set("owner_id", user_id)
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
