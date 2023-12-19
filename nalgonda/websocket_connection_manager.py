import asyncio

from starlette.websockets import WebSocket


class WebSocketConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []
        self._connections_lock = asyncio.Lock()

    async def connect(self, websocket: WebSocket):
        async with self._connections_lock:
            await websocket.accept()
            self.active_connections.append(websocket)

    async def disconnect(self, websocket: WebSocket):
        async with self._connections_lock:
            if websocket in self.active_connections:
                self.active_connections.remove(websocket)

    async def send_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)
