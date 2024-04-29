import asyncio
import logging
from datetime import UTC, datetime
from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from backend.dependencies.auth import get_current_user
from backend.dependencies.dependencies import get_agency_manager, get_session_manager, get_user_variable_manager
from backend.models.auth import User
from backend.models.message import Message
from backend.models.response_models import MessagePostData, MessagePostResponse
from backend.repositories.session_storage import SessionConfigStorage
from backend.services.agency_manager import AgencyManager
from backend.services.context_vars_manager import ContextEnvVarsManager
from backend.services.oai_client import get_openai_client
from backend.services.session_manager import SessionManager
from backend.services.user_variable_manager import UserVariableManager

logger = logging.getLogger(__name__)

message_router = APIRouter(
    responses={404: {"description": "Not found"}},
    tags=["message"],
)


@message_router.get("/message/list")
async def get_message_list(
    current_user: Annotated[User, Depends(get_current_user)],
    session_id: str,
    limit: int = 20,
    before: str | None = None,
    session_storage: SessionConfigStorage = Depends(SessionConfigStorage),
    user_variable_manager: UserVariableManager = Depends(get_user_variable_manager),
) -> list[Message]:
    """Get the list of messages for the given session_id."""
    # check if the current_user has permissions to send a message to the agency
    session_config = session_storage.load_by_id(session_id)
    if not session_config:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Session not found")
    if session_config.user_id != current_user.id:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN, detail="You don't have permissions to access this session"
        )

    # Set the user_id in the context variables
    ContextEnvVarsManager.set("user_id", current_user.id)

    # use OpenAI's Assistants API to get the messages by thread_id=session_id
    client = get_openai_client(user_variable_manager)
    messages = client.beta.threads.messages.list(thread_id=session_id, limit=limit, before=before, order="asc")
    messages_output = [
        Message(
            id=message.id,
            content=message.content[0].text.value if message.content and message.content[0].text else "[No content]",
            role=message.role,
            timestamp=datetime.fromtimestamp(message.created_at, tz=UTC).isoformat(),
            session_id=session_id,
            agency_id=session_config.agency_id,
        )
        for message in messages
    ]
    return messages_output


@message_router.post("/message")
async def post_message(
    current_user: Annotated[User, Depends(get_current_user)],
    request: Message,
    agency_manager: AgencyManager = Depends(get_agency_manager),
    session_manager: SessionManager = Depends(get_session_manager),
) -> MessagePostResponse:
    """Send a message to the User Proxy (the main agent) for the given agency_id and session_id."""
    agency_id = request.agency_id
    user_message = request.content
    session_id = request.session_id

    # Set the user_id and agency_id in the context variables
    ContextEnvVarsManager.set("user_id", current_user.id)
    ContextEnvVarsManager.set("agency_id", agency_id)

    logger.info(f"Received a message for agency_id: {agency_id}, session_id: {session_id}")

    session_config = session_manager.get_session(session_id)
    if not session_config:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Session not found")
    # permissions are checked in the agency_manager.get_agency method
    agency = await agency_manager.get_agency(agency_id, thread_ids=session_config.thread_ids, user_id=current_user.id)
    if not agency:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Agency not found")

    try:
        response = await asyncio.to_thread(
            agency.get_completion, message=user_message, yield_messages=False, message_files=None
        )
        return MessagePostResponse(data=MessagePostData(content=response))
    except Exception as e:
        logger.exception(f"Error sending message to agency {agency_id}, session {session_id}")
        raise HTTPException(status_code=500, detail="Something went wrong") from e
