import asyncio
import logging
from collections.abc import Callable

from agency_swarm import Agency
from fastapi import HTTPException, WebSocket, WebSocketDisconnect
from openai import AuthenticationError as OpenAIAuthenticationError
from websockets.exceptions import ConnectionClosedOK

from backend.constants import INTERNAL_ERROR_MESSAGE
from backend.exceptions import NotFoundError, UnsetVariableError
from backend.models.session_config import SessionConfig
from backend.services.agency_manager import AgencyManager
from backend.services.auth_service import AuthService
from backend.services.context_vars_manager import ContextEnvVarsManager
from backend.services.message_manager import MessageManager
from backend.services.session_manager import SessionManager
from backend.services.websocket.utils import get_next_response
from backend.services.websocket.websocket_connection_manager import WebSocketConnectionManager

logger = logging.getLogger(__name__)


class WebSocketHandler:
    def __init__(
        self,
        connection_manager: WebSocketConnectionManager,
        auth_service: AuthService,
        agency_manager: AgencyManager,
        message_manager: MessageManager,
        session_manager: SessionManager,
    ):
        self.connection_manager = connection_manager
        self.auth_service = auth_service
        self.agency_manager = agency_manager
        self.message_manager = message_manager
        self.session_manager = session_manager

    async def handle_websocket_connection(
        self,
        websocket: WebSocket,
        client_id: str,
    ) -> None:
        """
        Handle the WebSocket connection for a specific session.

        :param websocket: The WebSocket connection.
        :param client_id: The client ID.
        """
        await self.connection_manager.connect(websocket, client_id)
        logger.info(f"WebSocket connected for client_id: {client_id}")

        agency_id = None
        session_id = None
        try:
            message = await websocket.receive_json()
            user_id = message.get("user_id")
            agency_id = message.get("agency_id")
            session_id = message.get("session_id")
            token = message.get("token")

            if not user_id or not agency_id or not session_id or not token:
                await self.connection_manager.send_message(
                    {"status": "error", "message": "Missing required fields"}, client_id
                )
                return

            logger.info(
                f"WebSocket connected for client_id: {client_id}, agency_id: {agency_id}, "
                f"user_id: {user_id}, session_id: {session_id}"
            )

            await self._authenticate(client_id, user_id, token)

            session, agency = await self._setup_agency(agency_id, user_id, session_id)

            if not session or not agency:
                await self.connection_manager.send_message(
                    {"status": "error", "message": "Session not found" if not session else "Agency not found"},
                    client_id,
                )
                return

            await self._handle_websocket_messages(websocket, client_id, agency_id, agency, session_id, user_id)

        except (WebSocketDisconnect, ConnectionClosedOK):
            await self.connection_manager.disconnect(client_id)
            logger.info(f"WebSocket disconnected for client_id: {client_id}")
        except UnsetVariableError as exception:
            await self.connection_manager.send_message({"status": "error", "message": str(exception)}, client_id)
        except OpenAIAuthenticationError as exception:
            await self.connection_manager.send_message({"status": "error", "message": exception.message}, client_id)
        except NotFoundError as exception:
            await self.connection_manager.send_message({"status": "error", "message": str(exception)}, client_id)
        except Exception as exception:
            logger.exception(
                "Exception while processing message: "
                f"agency_id: {agency_id}, session_id: {session_id}, client_id: {client_id}, error: {str(exception)}"
            )
            await self.connection_manager.send_message(
                {"status": "error", "message": INTERNAL_ERROR_MESSAGE},
                client_id,
            )

    async def _authenticate(self, client_id: str, user_id: str, token: str) -> None:
        """Authenticate the user before sending messages.
        Process the token sent by the user and authenticate the user using Firebase.
        If the token is invalid, send an error message to the user.

        :param client_id: The client ID.
        :param user_id: The user ID.
        :param token: The token sent by the user.
        """
        try:
            self.auth_service.get_user(token)
        except HTTPException:
            logger.info(f"Invalid token for user_id: {user_id}")
            await self.connection_manager.send_message({"status": "error", "message": "Invalid token"}, client_id)
            raise WebSocketDisconnect from None
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
        agency, _ = await self.agency_manager.get_agency(agency_id, session_config.thread_ids, user_id)
        return session_config, agency

    async def _handle_websocket_messages(
        self,
        websocket: WebSocket,
        client_id: str,
        agency_id: str,
        agency: Agency,
        session_id: str,
        user_id: str,
    ) -> None:
        """
        Handle the WebSocket messages for a specific session.

        :param websocket: The WebSocket connection.
        :param client_id: The client ID.
        :param agency_id: The agency ID.
        :param agency: The agency instance.
        :param session_id: The session ID.
        :param user_id: The user ID.
        """
        while await self._process_messages(websocket, client_id, agency_id, agency, session_id, user_id):
            pass

    async def _process_messages(
        self,
        websocket: WebSocket,
        client_id: str,
        agency_id: str,
        agency: Agency,
        session_id: str,
        user_id: str,
    ) -> bool:
        """
        Receive messages from the websocket and process them.

        :param websocket: The WebSocket connection.
        :param client_id: The client ID.
        :param agency_id: The agency ID.
        :param agency: The agency instance.
        :param session_id: The session ID.
        :param user_id: The user ID.

        :return: True if the processing should continue, False otherwise.
        """
        try:
            await self._process_single_message(websocket, client_id, agency_id, agency, session_id, user_id)
        except UnsetVariableError as exception:
            await self.connection_manager.send_message({"status": "error", "message": str(exception)}, client_id)
            return False
        except OpenAIAuthenticationError as exception:
            await self.connection_manager.send_message({"status": "error", "message": exception.message}, client_id)
            return False
        return True

    async def _process_single_message(
        self, websocket: WebSocket, client_id: str, agency_id: str, agency: Agency, session_id: str, user_id: str
    ) -> None:
        """
        Process a single user message and send the response to the websocket.

        :param websocket: The WebSocket connection.
        :param agency_id: The agency ID.
        :param agency: The agency instance.
        :param user_id: The user ID.
        """
        message = await websocket.receive_json()
        message_type = message.get("type")
        message_data = message.get("data")

        if message_type == "user_message":
            user_message = message_data.get("message")
            if not user_message:
                await self.connection_manager.send_message(
                    {"status": "error", "message": "Message not provided"}, client_id
                )
                return

            self.session_manager.update_session_timestamp(session_id)

            loop = asyncio.get_running_loop()
            response_generator = agency.get_completion(message=user_message, yield_messages=True)

            while await self._process_single_message_response(
                lambda: get_next_response(response_generator, user_id, agency_id), client_id, loop
            ):
                pass

            all_messages = self.message_manager.get_messages(session_id)
            response = {
                "status": True,
                "message": "Message processed successfully",
                "data": all_messages,
            }
            await self.connection_manager.send_message(
                {"type": "agent_response", "data": response, "connection_id": client_id},
                client_id,
            )
        else:
            await self.connection_manager.send_message(
                {"status": "error", "message": "Invalid message type"}, client_id
            )

    async def _process_single_message_response(
        self, get_next_response_func: Callable, client_id: str, loop: asyncio.AbstractEventLoop
    ) -> bool:
        """
        Process a single message response and send it to the websocket.

        :param get_next_response_func: A function to get the next response.
        :param client_id: The client ID.
        :param loop: The event loop.

        :return: True if there are more responses to send, False otherwise.
        """
        response = await loop.run_in_executor(None, get_next_response_func)
        if response is None:
            return False

        response_text = response.get_formatted_content()
        await self.connection_manager.send_message({"type": "agent_message", "data": response_text}, client_id)
        return True
