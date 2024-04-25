import logging

from fastapi import APIRouter, Depends, WebSocket

from backend.dependencies.dependencies import get_websocket_handler
from backend.services.websocket_handler import WebSocketHandler

logger = logging.getLogger(__name__)

websocket_router = APIRouter(
    tags=["websocket"],
    responses={404: {"description": "Not found"}},
)


@websocket_router.websocket("/ws/{user_id}/{agency_id}/{session_id}")
async def websocket_session_endpoint(
    websocket: WebSocket,
    user_id: str,
    agency_id: str,
    session_id: str,
    websocket_handler: WebSocketHandler = Depends(get_websocket_handler),
) -> None:
    """
    WebSocket endpoint for maintaining conversation with a specific session.
    Send messages to and from the userproxy of the given agency.

    :param websocket: The WebSocket connection.
    :param user_id: The user ID associated with the session.
    :param agency_id: The agency ID associated with the session.
    :param session_id: The session ID.
    :param websocket_handler: The WebSocket handler instance.
    """
    await websocket_handler.handle_websocket_connection(websocket, user_id, agency_id, session_id)
