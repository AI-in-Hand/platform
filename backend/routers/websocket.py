import logging

from fastapi import APIRouter, Depends

from backend.dependencies.dependencies import get_websocket, get_websocket_handler
from backend.services.websocket.websocket_handler import WebSocketHandler

logger = logging.getLogger(__name__)

websocket_router = APIRouter(
    tags=["websocket"],
    responses={404: {"description": "Not found"}},
)


@websocket_router.websocket("/{client_id}")
async def websocket_session_endpoint(
    client_id: str,
    websocket=Depends(get_websocket),
    websocket_handler: WebSocketHandler = Depends(get_websocket_handler),
) -> None:
    """
    WebSocket endpoint for maintaining conversation with a specific session.
    Send messages to and from the userproxy of the given agency.

    :param client_id: The client ID.
    :param websocket: The WebSocket connection.
    :param websocket_handler: The WebSocket handler instance.
    """
    await websocket_handler.handle_websocket_connection(websocket, client_id)
