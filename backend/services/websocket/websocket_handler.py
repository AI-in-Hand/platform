import asyncio
import logging
from collections.abc import Callable

from agency_swarm import Agency
from fastapi import HTTPException, WebSocket, WebSocketDisconnect
from websockets.exceptions import ConnectionClosedOK

from backend.models.session_config import SessionConfig
from backend.services.agency_manager import AgencyManager
from backend.services.auth_service import AuthService
from backend.services.context_vars_manager import ContextEnvVarsManager
from backend.services.session_manager import SessionManager
from backend.services.websocket.utils import get_next_response
from backend.services.websocket.websocket_connection_manager import WebSocketConnectionManager

logger = logging.getLogger(__name__)


class WebSocketHandler:
    def __init__(
        self,
        connection_manager: WebSocketConnectionManager,
        auth_service: AuthService,
        session_manager: SessionManager,
        agency_manager: AgencyManager,
    ):
        self.connection_manager = connection_manager
        self.auth_service = auth_service
        self.session_manager = session_manager
        self.agency_manager = agency_manager

    async def handle_websocket_connection(
        self,
        websocket: WebSocket,
        user_id: str,
        agency_id: str,
        session_id: str,
    ) -> None:
        """
        Handle the WebSocket connection for a specific session.

        :param websocket: The WebSocket connection.
        :param user_id: The user ID associated with the session.
        :param agency_id: The agency ID associated with the session.
        :param session_id: The session ID.
        """
        await self.connection_manager.connect(websocket)
        logger.info(f"WebSocket connected for agency_id: {agency_id}, session_id: {session_id}")

        await self._authenticate(websocket, user_id)

        session, agency = await self._setup_agency(agency_id, user_id, session_id)

        if not session or not agency:
            await self.connection_manager.send_message(
                "Session not found" if not session else "Agency not found", websocket
            )
            await self.connection_manager.disconnect(websocket)
            return

        await self._handle_websocket_messages(websocket, agency_id, agency, session_id, user_id)
        await self.connection_manager.disconnect(websocket)
        logger.info(f"WebSocket disconnected for agency_id: {agency_id}")

    async def _authenticate(self, websocket: WebSocket, user_id: str) -> None:
        """Authenticate the user before sending messages.
        Process the token sent by the user and authenticate the user using Firebase.
        If the token is invalid, send an error message to the user.
        """
        token = await websocket.receive_text()
        try:
            self.auth_service.get_user(token)
        except HTTPException:
            await self.connection_manager.send_message("Invalid token", websocket)
            await self.connection_manager.disconnect(websocket)
            return
        ContextEnvVarsManager.set("user_id", user_id)

    async def _setup_agency(
        self, agency_id: str, user_id: str, session_id: str
    ) -> tuple[SessionConfig | None, Agency | None]:
        """
        Set up the agency and thread IDs for the WebSocket connection.

        :param agency_id: The agency ID.
        :param user_id: The user ID.
        :param session_id: The session ID.

        :return: The session config and agency instances.
        """
        session_config = self.session_manager.get_session(session_id)
        if not session_config:
            return session_config, None
        agency = await self.agency_manager.get_agency(agency_id, session_config.thread_ids, user_id)
        return session_config, agency

    async def _handle_websocket_messages(
        self,
        websocket: WebSocket,
        agency_id: str,
        agency: Agency,
        session_id: str,
        user_id: str,
    ) -> None:
        """
        Handle the WebSocket messages for a specific session.

        :param websocket: The WebSocket connection.
        :param agency_id: The agency ID.
        :param agency: The agency instance.
        :param session_id: The session ID.
        :param user_id: The user ID.
        """
        while await self._process_messages(websocket, agency_id, agency, session_id, user_id):
            pass

    async def _process_messages(
        self,
        websocket: WebSocket,
        agency_id: str,
        agency: Agency,
        session_id: str,
        user_id: str,
    ) -> bool:
        """
        Receive messages from the websocket and process them.

        :param websocket: The WebSocket connection.
        :param agency_id: The agency ID.
        :param agency: The agency instance.
        :param session_id: The session ID.
        :param user_id: The user ID.

        :return: True if the processing should continue, False otherwise.
        """
        try:
            await self._process_single_message(websocket, agency_id, agency, user_id)
        except (WebSocketDisconnect, ConnectionClosedOK):
            return False
        except Exception as exception:
            logger.exception(
                "Exception while processing message: "
                f"agency_id: {agency_id}, session_id: {session_id}, error: {str(exception)}"
            )
            await self.connection_manager.send_message("Something went wrong. Please try again.", websocket)
        return True

    async def _process_single_message(self, websocket: WebSocket, agency_id: str, agency: Agency, user_id: str) -> None:
        """
        Process a single user message and send the response to the websocket.

        :param websocket: The WebSocket connection.
        :param agency_id: The agency ID.
        :param agency: The agency instance.
        :param user_id: The user ID.
        """
        user_message = await websocket.receive_text()
        if not user_message.strip():
            await self.connection_manager.send_message("Message not provided", websocket)
            return

        loop = asyncio.get_running_loop()
        response_generator = agency.get_completion(message=user_message, yield_messages=True)

        while await self._process_single_message_response(
            lambda: get_next_response(response_generator, user_id, agency_id), websocket, loop
        ):
            pass

    async def _process_single_message_response(
        self, get_next_response: Callable, websocket: WebSocket, loop: asyncio.AbstractEventLoop
    ) -> bool:
        """
        Process a single message response and send it to the websocket.

        :param get_next_response: A function to get the next response.
        :param websocket: The WebSocket connection.
        :param loop: The event loop.

        :return: True if there are more responses to send, False otherwise.
        """
        response = await loop.run_in_executor(None, get_next_response)
        if response is None:
            return False

        response_text = response.get_formatted_content()
        await self.connection_manager.send_message(response_text, websocket)
        return True
