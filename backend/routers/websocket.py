import asyncio
import logging
from typing import Any

from agency_swarm import Agency
from agency_swarm.messages import MessageOutput
from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from websockets.exceptions import ConnectionClosedOK

from backend.dependencies.dependencies import get_agency_manager, get_session_manager
from backend.models.session_config import SessionConfig
from backend.services.agency_manager import AgencyManager
from backend.services.context_vars_manager import ContextEnvVarsManager
from backend.services.session_manager import SessionManager
from backend.services.websocket_connection_manager import WebSocketConnectionManager

logger = logging.getLogger(__name__)

websocket_router = APIRouter(
    tags=["websocket"],
    responses={404: {"description": "Not found"}},
)


class WebSocketHandler:
    def __init__(self, connection_manager: WebSocketConnectionManager):
        self.connection_manager = connection_manager

    async def connect(self, websocket: WebSocket) -> None:
        await self.connection_manager.connect(websocket)

    async def disconnect(self, websocket: WebSocket) -> None:
        await self.connection_manager.disconnect(websocket)

    async def get_agency(
        self, agency_manager: AgencyManager, agency_id: str, thread_ids: dict[str, Any], user_id: str
    ) -> Agency | None:
        return await agency_manager.get_agency(agency_id, thread_ids, user_id)

    async def process_single_message(
        self, user_message: str, agency: Agency, websocket: WebSocket, user_id: str, agency_id: str
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
            await self.connection_manager.send_message(response_text, websocket)

    async def process_messages(
        self,
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
                    await self.connection_manager.send_message("Message not provided", websocket)
                    continue

                await self.process_single_message(user_message, agency, websocket, user_id, agency_id)

            except (WebSocketDisconnect, ConnectionClosedOK) as e:
                raise e
            except Exception as e:
                logger.exception(
                    "Exception while processing message: "
                    f"agency_id: {agency_id}, session_id: {session_id}, error: {str(e)}"
                )
                await self.connection_manager.send_message("Something went wrong. Please try again.", websocket)
                continue

    async def setup_agency(
        self,
        agency_id: str,
        user_id: str,
        session_id: str,
        agency_manager: AgencyManager,
        session_manager: SessionManager,
    ) -> tuple[SessionConfig | None, Agency | None]:
        """Set up the agency and thread IDs for the WebSocket connection."""
        session = session_manager.get_session(session_id)
        if not session:
            return session, None
        agency = await self.get_agency(agency_manager, agency_id, session.thread_ids, user_id)
        return session, agency

    async def handle_websocket_messages(
        self,
        websocket: WebSocket,
        agency_id: str,
        session_id: str,
        user_id: str,
        agency: Agency,
    ) -> None:
        """Handle the WebSocket messages for a specific session."""
        try:
            await self.process_messages(websocket, agency_id, agency, session_id, user_id)
        except (WebSocketDisconnect, ConnectionClosedOK):
            await self.disconnect(websocket)
            logger.info(f"WebSocket disconnected for agency_id: {agency_id}")

    async def handle_websocket_connection(
        self,
        websocket: WebSocket,
        user_id: str,
        agency_id: str,
        session_id: str,
        agency_manager: AgencyManager,
        session_manager: SessionManager,
    ) -> None:
        """Handle the WebSocket connection for a specific session."""
        await self.connect(websocket)
        logger.info(f"WebSocket connected for agency_id: {agency_id}, session_id: {session_id}")

        ContextEnvVarsManager.set("user_id", user_id)

        session, agency = await self.setup_agency(agency_id, user_id, session_id, agency_manager, session_manager)
        if not session or not agency:
            await self.connection_manager.send_message(
                "Session not found" if not session else "Agency not found", websocket
            )
            await self.disconnect(websocket)
            return

        await self.handle_websocket_messages(websocket, agency_id, session_id, user_id, agency)


@websocket_router.websocket("/ws/{user_id}/{agency_id}/{session_id}")
async def websocket_session_endpoint(
    websocket: WebSocket,
    user_id: str,
    agency_id: str,
    session_id: str,
    agency_manager: AgencyManager = Depends(get_agency_manager),
    session_manager: SessionManager = Depends(get_session_manager),
    websocket_handler: WebSocketHandler = Depends(lambda: WebSocketHandler(WebSocketConnectionManager())),
) -> None:
    """WebSocket endpoint for maintaining conversation with a specific session.
    Send messages to and from CEO of the given agency."""
    # TODO: Add authentication: validate user_id using the token

    await websocket_handler.handle_websocket_connection(
        websocket, user_id, agency_id, session_id, agency_manager, session_manager
    )
