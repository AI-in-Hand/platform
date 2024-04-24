import asyncio
import logging
from typing import Any

from agency_swarm import Agency
from agency_swarm.messages import MessageOutput
from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from websockets.exceptions import ConnectionClosedOK

from backend.dependencies.dependencies import get_agency_manager
from backend.services.agency_manager import AgencyManager
from backend.services.context_vars_manager import ContextEnvVarsManager
from backend.services.websocket_connection_manager import WebSocketConnectionManager

logger = logging.getLogger(__name__)

connection_manager = WebSocketConnectionManager()
websocket_router = APIRouter(
    tags=["websocket"],
    responses={404: {"description": "Not found"}},
)


async def connect_websocket(websocket: WebSocket) -> None:
    await connection_manager.connect(websocket)


async def disconnect_websocket(websocket: WebSocket) -> None:
    await connection_manager.disconnect(websocket)


async def get_agency(
    agency_manager: AgencyManager, agency_id: str, thread_ids: dict[str, Any], user_id: str
) -> Agency | None:
    return await agency_manager.get_agency(agency_id, thread_ids, user_id)


async def process_single_message(
    user_message: str, agency: Agency, websocket: WebSocket, user_id: str, agency_id: str
) -> None:
    """Process a single user message and send the response to the websocket."""
    loop = asyncio.get_running_loop()

    gen = agency.get_completion(message=user_message, yield_messages=True)

    def get_next_response() -> MessageOutput | None:
        try:
            # Set the user_id and agency_id in the context variables
            ContextEnvVarsManager.set("user_id", user_id)
            ContextEnvVarsManager.set("agency_id", agency_id)
            return next(gen)
        except StopIteration:
            return None

    while True:
        response = await loop.run_in_executor(None, get_next_response)
        if response is None:
            break

        response_text = response.get_formatted_content()
        await connection_manager.send_message(response_text, websocket)


async def process_messages(
    websocket: WebSocket,
    agency_id: str,
    agency: Agency,
    session_id: str,
    user_id: str,
) -> None:
    """Receive messages from the websocket and process them."""
    while True:
        try:
            user_message = await websocket.receive_text()

            if not user_message.strip():
                await connection_manager.send_message("Message not provided", websocket)
                continue

            await process_single_message(user_message, agency, websocket, user_id, agency_id)

        except (WebSocketDisconnect, ConnectionClosedOK) as e:
            raise e
        except Exception as e:
            logger.exception(
                f"Exception while processing message: agency_id: {agency_id}, session_id: {session_id}, error: {str(e)}"
            )
            await connection_manager.send_message("Something went wrong. Please try again.", websocket)
            continue


async def setup_agency(
    agency_manager: AgencyManager, agency_id: str, user_id: str
) -> tuple[Agency | None, dict[str, Any]]:
    """Set up the agency and thread IDs for the WebSocket connection."""
    thread_ids: dict[str, Any] = {}  # for chat persistence, need to save/load these thread_ids
    agency = await get_agency(agency_manager, agency_id, thread_ids, user_id)
    return agency, thread_ids


async def handle_websocket_messages(
    websocket: WebSocket,
    agency_id: str,
    session_id: str,
    user_id: str,
    agency: Agency,
) -> None:
    """Handle the WebSocket messages for a specific session."""
    try:
        await process_messages(websocket, agency_id, agency, session_id, user_id)
    except (WebSocketDisconnect, ConnectionClosedOK):
        await disconnect_websocket(websocket)
        logger.info(f"WebSocket disconnected for agency_id: {agency_id}")


async def handle_websocket_connection(
    websocket: WebSocket,
    user_id: str,
    agency_id: str,
    session_id: str,
    agency_manager: AgencyManager,
) -> None:
    """Handle the WebSocket connection for a specific session."""
    await connect_websocket(websocket)
    logger.info(f"WebSocket connected for agency_id: {agency_id}, session_id: {session_id}")

    ContextEnvVarsManager.set("user_id", user_id)

    agency, _ = await setup_agency(agency_manager, agency_id, user_id)
    if not agency:
        await connection_manager.send_message("Agency not found", websocket)
        await disconnect_websocket(websocket)
        return

    await handle_websocket_messages(websocket, agency_id, session_id, user_id, agency)


@websocket_router.websocket("/ws/{user_id}/{agency_id}/{session_id}")
async def websocket_session_endpoint(
    websocket: WebSocket,
    user_id: str,
    agency_id: str,
    session_id: str,
    agency_manager: AgencyManager = Depends(get_agency_manager),
) -> None:
    """WebSocket endpoint for maintaining conversation with a specific session.
    Send messages to and from CEO of the given agency."""
    # TODO: Add authentication: validate user_id using the token

    await handle_websocket_connection(websocket, user_id, agency_id, session_id, agency_manager)
