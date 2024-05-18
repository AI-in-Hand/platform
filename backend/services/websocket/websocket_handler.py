import asyncio
import logging

from agency_swarm import Agency
from fastapi import HTTPException, WebSocket, WebSocketDisconnect
from openai import AuthenticationError as OpenAIAuthenticationError
from openai.lib.streaming import AssistantEventHandler
from openai.types.beta.threads import Text, TextDelta
from openai.types.beta.threads.runs import ToolCall, ToolCallDelta
from typing_extensions import override
from websockets.exceptions import ConnectionClosedOK

from backend.constants import INTERNAL_ERROR_MESSAGE
from backend.exceptions import NotFoundError, UnsetVariableError
from backend.models.auth import User
from backend.models.session_config import SessionConfig
from backend.services.agency_manager import AgencyManager
from backend.services.auth_service import AuthService
from backend.services.context_vars_manager import ContextEnvVarsManager
from backend.services.message_manager import MessageManager
from backend.services.session_manager import SessionManager
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

        try:
            await self._handle_websocket_messages(websocket, client_id)

        except (WebSocketDisconnect, ConnectionClosedOK):
            await self.connection_manager.disconnect(client_id)
            logger.info(f"WebSocket disconnected for client_id: {client_id}")
        except UnsetVariableError as exception:
            await self.connection_manager.send_message({"status": False, "message": str(exception)}, client_id)
        except OpenAIAuthenticationError as exception:
            await self.connection_manager.send_message({"status": False, "message": exception.message}, client_id)
        except NotFoundError as exception:
            await self.connection_manager.send_message({"status": False, "message": str(exception)}, client_id)
        except Exception as exception:
            logger.exception("Exception while processing message: " f"client_id: {client_id}, error: {str(exception)}")
            await self.connection_manager.send_message(
                {"status": False, "message": INTERNAL_ERROR_MESSAGE},
                client_id,
            )

    async def _authenticate(self, client_id: str, token: str) -> User:
        """Authenticate the user before sending messages.
        Process the token sent by the user and authenticate the user using Firebase.
        If the token is invalid, send an error message to the user.

        :param client_id: The client ID.
        :param token: The token sent by the user.
        """
        try:
            user = self.auth_service.get_user(token)
        except HTTPException:
            logger.info(f"Invalid token {token} for client_id: {client_id}")
            await self.connection_manager.send_message({"status": False, "message": "Invalid token"}, client_id)
            raise WebSocketDisconnect from None

        ContextEnvVarsManager.set("user_id", user.id)
        return user

    async def _setup_agency(self, user_id: str, session_id: str) -> tuple[SessionConfig | None, Agency | None]:
        """
        Set up the agency and thread IDs for the WebSocket connection.

        :param user_id: The user ID.
        :param session_id: The session ID.

        :return: The session config and agency instances.
        """
        session = self.session_manager.get_session(session_id)
        agency, _ = await self.agency_manager.get_agency(session.agency_id, session.thread_ids, user_id)
        ContextEnvVarsManager.set("agency_id", session.agency_id)
        return session, agency

    async def _handle_websocket_messages(
        self,
        websocket: WebSocket,
        client_id: str,
    ) -> None:
        """
        Handle the WebSocket messages for a specific session.

        :param websocket: The WebSocket connection.
        :param client_id: The client ID.
        """
        while await self._process_messages(websocket, client_id):
            pass

    async def _process_messages(
        self,
        websocket: WebSocket,
        client_id: str,
    ) -> bool:
        """
        Receive messages from the websocket and process them.

        :param websocket: The WebSocket connection.
        :param client_id: The client ID.

        :return: True if the processing should continue, False otherwise.
        """
        try:
            await self._process_single_message(websocket, client_id)
        except UnsetVariableError as exception:
            await self.connection_manager.send_message({"status": False, "message": str(exception)}, client_id)
            return False
        except OpenAIAuthenticationError as exception:
            await self.connection_manager.send_message({"status": False, "message": exception.message}, client_id)
            return False
        return True

    async def _process_single_message(self, websocket: WebSocket, client_id: str) -> None:
        """
        Process a single user message and send the response to the websocket.

        :param websocket: The WebSocket connection.
        :param client_id: The client ID.
        """
        connection_manager = self.connection_manager

        class WebSocketEventHandler(AssistantEventHandler):
            agent_name = None
            recipient_agent_name = None

            @override
            def on_text_created(self, text: Text) -> None:  # type: ignore
                """Callback that is fired when a text content block is created"""
                asyncio.create_task(
                    connection_manager.send_message(
                        {
                            "type": "agent_status",
                            "data": {"message": f"\n{self.recipient_agent_name} @ {self.agent_name}  > "},
                        },
                        client_id,
                    )
                )

            @override
            def on_text_delta(self, delta: TextDelta, snapshot: Text) -> None:  # type: ignore
                """Callback that is fired whenever a text content delta is returned
                by the API.
                """
                asyncio.create_task(
                    connection_manager.send_message(
                        {"type": "agent_status", "data": {"message": delta.value}},
                        client_id,
                    )
                )

            @override
            def on_text_done(self, text: Text) -> None:  # type: ignore
                """Callback that is fired when a text content block is done"""
                asyncio.create_task(
                    connection_manager.send_message(
                        {
                            "type": "agent_message",
                            "data": {
                                "sender": self.recipient_agent_name,
                                "recipient": self.agent_name,
                                "message": {"content": text.value},
                            },
                        },
                        client_id,
                    )
                )

            def on_tool_call_created(self, tool_call: ToolCall) -> None:
                """Callback that is fired when a tool call is created"""
                asyncio.create_task(
                    connection_manager.send_message(
                        {
                            "type": "agent_status",
                            "data": {"message": f"\n{self.recipient_agent_name} > {tool_call.type}\n"},
                        },
                        client_id,
                    )
                )

            def on_tool_call_delta(self, delta: ToolCallDelta, snapshot: ToolCall) -> None:  # noqa:  ARG002
                """Callback that is fired when a tool call delta is encountered"""
                if delta.type == "code_interpreter":
                    if delta.code_interpreter.input:
                        asyncio.create_task(
                            connection_manager.send_message(
                                {"type": "agent_status", "data": {"message": delta.code_interpreter.input}},
                                client_id,
                            )
                        )
                    if delta.code_interpreter.outputs:
                        asyncio.create_task(
                            connection_manager.send_message(
                                {"type": "agent_status", "data": {"message": "\n\noutput > "}},
                                client_id,
                            )
                        )
                        for output in delta.code_interpreter.outputs:
                            if output.type == "logs":
                                asyncio.create_task(
                                    connection_manager.send_message(
                                        {"type": "agent_status", "data": {"message": f"\n{output.logs}"}},
                                        client_id,
                                    )
                                )

            @classmethod
            def on_all_streams_end(cls):
                """Fires when streams for all agents have ended."""
                pass  # Handled in WebSocketHandler._process_single_message

        message = await websocket.receive_json()
        message_type = message.get("type")
        message_data = message.get("data")
        token = message.get("access_token")

        if not token:
            await self.connection_manager.send_message(
                {"status": False, "message": "Access token not provided"}, client_id
            )
            return

        user = await self._authenticate(client_id, token)

        if message_type == "user_message":
            user_message = message_data.get("content")
            session_id = message_data.get("session_id")

            if not user_message or not session_id:
                await self.connection_manager.send_message(
                    {"status": False, "message": "Message or session ID not provided"}, client_id
                )
                return

            session, agency = await self._setup_agency(user.id, session_id)

            if not session or not agency:
                await self.connection_manager.send_message(
                    {"status": False, "message": "Session not found" if not session else "Agency not found"},
                    client_id,
                )
                return

            self.session_manager.update_session_timestamp(session_id)

            def get_completion_stream_wrapper():
                # Set the user_id and agency_id in the context variables
                ContextEnvVarsManager.set("user_id", user.id)
                ContextEnvVarsManager.set("agency_id", session.agency_id)
                agency.get_completion_stream(user_message, WebSocketEventHandler)

            loop = asyncio.get_running_loop()
            await loop.run_in_executor(
                None,
                get_completion_stream_wrapper,
            )

            all_messages = self.message_manager.get_messages(session_id)
            all_messages_dict = [message.model_dump() for message in all_messages]
            response = {
                "status": True,
                "message": "Message processed successfully",
                "data": all_messages_dict,
            }
            await self.connection_manager.send_message(
                {"type": "agent_response", "data": response, "connection_id": client_id},
                client_id,
            )
        else:
            await self.connection_manager.send_message({"status": False, "message": "Invalid message type"}, client_id)
