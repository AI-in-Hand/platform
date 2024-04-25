import pytest
from starlette.websockets import WebSocketDisconnect

from backend.dependencies.dependencies import get_websocket_handler
from backend.main import ws_app


@pytest.fixture
def mock_websocket_handler():
    class MockWebSocketHandler:
        def __init__(self, *args, **kwargs):
            pass

        async def handle_websocket_connection(self, websocket, user_id, agency_id, session_id):  # noqa: ARG002
            await websocket.accept()
            try:
                while True:
                    data = await websocket.receive_text()
                    await websocket.send_text(f"Echo: {data}")
            except WebSocketDisconnect:
                await websocket.close()

    ws_app.dependency_overrides[get_websocket_handler] = lambda: MockWebSocketHandler()
    yield
    ws_app.dependency_overrides[get_websocket_handler] = get_websocket_handler


@pytest.mark.usefixtures("mock_websocket_handler")
def test_websocket_connection(client):
    with client.websocket_connect("/ws/user123/agency456/session789") as websocket:
        websocket.send_text("Hello WebSocket")
        data = websocket.receive_text()
        websocket.close()
        assert data == "Echo: Hello WebSocket"
