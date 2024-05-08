import asyncio

from starlette.websockets import WebSocket


class WebSocketConnectionManager:
    def __init__(self) -> None:
        self.active_connections: dict[str, WebSocket] = {}
        self._connections_lock = asyncio.Lock()

    async def connect(self, websocket: WebSocket, client_id: str) -> None:
        async with self._connections_lock:
            await websocket.accept()
            self.active_connections[client_id] = websocket

    async def disconnect(self, client_id: str, close: bool = False) -> None:
        async with self._connections_lock:
            if client_id in self.active_connections:
                websocket = self.active_connections.pop(client_id)
                if close:
                    await websocket.close()

    async def send_message(self, message: dict, client_id: str) -> None:
        async with self._connections_lock:
            if client_id in self.active_connections:
                websocket = self.active_connections[client_id]
                await websocket.send_json(message)
