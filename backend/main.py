import json
import logging
import uuid

from fastapi import FastAPI, WebSocket, WebSocketDisconnect

from base_agency.agency_manager import create_agency, get_agency
from constants import DATA_DIR

# Ensure directories exist
DATA_DIR.mkdir(exist_ok=True)

app = FastAPI()
logger = logging.getLogger(__name__)


@app.get("/start")
async def start():
    session_id = uuid.uuid4().hex
    create_agency(session_id)
    return {"session_id": session_id}


class ConnectionManager:
    def __init__(self):
        self.active_connections = {}  # session_id: websocket

    async def connect(self, websocket: WebSocket, session_id: str):
        await websocket.accept()
        self.active_connections[session_id] = websocket

    def disconnect(self, session_id: str):
        if session_id in self.active_connections:
            del self.active_connections[session_id]

    async def send_message(self, message: str, session_id: str):
        websocket = self.active_connections.get(session_id)
        if websocket:
            await websocket.send_text(message)


manager = ConnectionManager()


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    session_id = ""  # Initialize session_id

    try:
        while True:
            data = await websocket.receive_text()
            try:
                message_data = json.loads(data)
                session_id = message_data.get("session_id")
                user_message = message_data.get("message")

                if not session_id or not user_message:
                    await websocket.close(code=1003)
                    return

                if session_id not in manager.active_connections:
                    await manager.connect(websocket, session_id)

                agency = get_agency(session_id)

                gen = agency.get_completion(message=user_message)
                for response in gen:
                    await manager.send_message(response, session_id)

            except json.JSONDecodeError:
                logger.error("Invalid JSON received")
                await websocket.close(code=1003)

    except WebSocketDisconnect:
        manager.disconnect(session_id)
        logger.info("WebSocket disconnected")
