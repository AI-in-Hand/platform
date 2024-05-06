import pytest
from starlette.websockets import WebSocketDisconnect

from backend.dependencies.dependencies import get_websocket_handler
from backend.main import ws_app


@pytest.fixture
def mock_websocket_handler():
    class MockWebSocketHandler:
        def __init__(self, *args, **kwargs):
            pass

        async def handle_websocket_connection(self, websocket, client_id):  # noqa: ARG002
            await websocket.accept()
            try:
                while True:
                    data = await websocket.receive_json()
                    await websocket.send_json({"message": f"Echo: {data['message']}"})
            except WebSocketDisconnect:
                await websocket.close()

    ws_app.dependency_overrides[get_websocket_handler] = lambda: MockWebSocketHandler()
    yield
    ws_app.dependency_overrides[get_websocket_handler] = get_websocket_handler


@pytest.mark.usefixtures("mock_websocket_handler")
def test_websocket_connection(client):
    with client.websocket_connect("/ws/client_id") as websocket:
        websocket.send_json({"message": "Hello WebSocket"})
        data = websocket.receive_json()
        websocket.close()
        assert data["message"] == "Echo: Hello WebSocket"
