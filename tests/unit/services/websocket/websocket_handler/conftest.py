from unittest.mock import AsyncMock, MagicMock

import pytest

from backend.services.websocket.websocket_handler import WebSocketHandler


@pytest.fixture
def websocket_handler():
    connection_manager = AsyncMock()
    auth_service = MagicMock()
    agency_manager = AsyncMock()
    message_manager = MagicMock()
    session_manager = MagicMock()
    return WebSocketHandler(connection_manager, auth_service, agency_manager, message_manager, session_manager)
