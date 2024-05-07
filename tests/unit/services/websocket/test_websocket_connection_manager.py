import asyncio

import pytest

from backend.services.websocket.websocket_connection_manager import WebSocketConnectionManager


class MockWebSocket:
    def __init__(self):
        self.accepted_subprotocol = None
        self.sent_json = None

    async def accept(self):
        pass

    async def close(self):
        self.accepted_subprotocol = None

    async def send_json(self, message):
        self.sent_json = message


@pytest.fixture
def connection_manager():
    return WebSocketConnectionManager()


@pytest.fixture
def mock_websocket():
    return MockWebSocket()


@pytest.mark.asyncio
async def test_connect(connection_manager, mock_websocket):
    client_id = "client1"
    await connection_manager.connect(mock_websocket, client_id)
    assert client_id in connection_manager.active_connections
    assert connection_manager.active_connections[client_id] == mock_websocket


@pytest.mark.asyncio
async def test_disconnect(connection_manager, mock_websocket):
    client_id = "client1"
    await connection_manager.connect(mock_websocket, client_id)
    await connection_manager.disconnect(client_id)
    assert client_id not in connection_manager.active_connections


@pytest.mark.asyncio
async def test_disconnect_with_close(connection_manager, mock_websocket):
    client_id = "client1"
    await connection_manager.connect(mock_websocket, client_id)
    await connection_manager.disconnect(client_id, close=True)
    assert client_id not in connection_manager.active_connections
    assert mock_websocket.accepted_subprotocol is None


@pytest.mark.asyncio
async def test_disconnect_nonexistent_client(connection_manager):
    client_id = "nonexistent_client"
    await connection_manager.disconnect(client_id)
    assert client_id not in connection_manager.active_connections


@pytest.mark.asyncio
async def test_send_message(connection_manager, mock_websocket):
    client_id = "client1"
    await connection_manager.connect(mock_websocket, client_id)
    message = {"text": "Hello"}
    await connection_manager.send_message(message, client_id)
    assert mock_websocket.sent_json == message


@pytest.mark.asyncio
async def test_send_message_nonexistent_client(connection_manager):
    client_id = "nonexistent_client"
    message = {"text": "Hello"}
    await connection_manager.send_message(message, client_id)
    assert client_id not in connection_manager.active_connections


@pytest.mark.asyncio
async def test_concurrent_connections(connection_manager):
    websocket1 = MockWebSocket()
    websocket2 = MockWebSocket()
    client_id1 = "client1"
    client_id2 = "client2"
    await asyncio.gather(
        connection_manager.connect(websocket1, client_id1),
        connection_manager.connect(websocket2, client_id2),
    )
    assert client_id1 in connection_manager.active_connections
    assert client_id2 in connection_manager.active_connections
    assert connection_manager.active_connections[client_id1] == websocket1
    assert connection_manager.active_connections[client_id2] == websocket2
