import json
import logging
import uuid

from fastapi import FastAPI, WebSocket, WebSocketDisconnect

from base_agency.agency_manager import AgencyManager
from constants import DATA_DIR

# Ensure directories exist
DATA_DIR.mkdir(exist_ok=True)

app = FastAPI()
logger = logging.getLogger(__name__)

agency_manager = AgencyManager()


@app.get("/start")
async def start():
    session_id = uuid.uuid4().hex
    agency_manager.create_agency(session_id)
    return {"session_id": session_id}


class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[str, WebSocket] = {}  # session_id: websocket

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


ws_manager = ConnectionManager()


@app.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    logger.info(f"WebSocket connected for session_id: {session_id}")
    await ws_manager.connect(websocket, session_id)

    try:
        while True:
            user_message = await websocket.receive_text()
            try:
                if not user_message:
                    await ws_manager.send_message("message not provided", session_id)
                    ws_manager.disconnect(session_id)
                    await websocket.close(code=1003)
                    return

                agency = agency_manager.get_agency(session_id)

                gen = agency.get_completion(message=user_message)
                for response in gen:
                    response_text = response.get_formatted_content()
                    await ws_manager.send_message(response_text, session_id)

            except json.JSONDecodeError:
                logger.error("Invalid JSON received")
                ws_manager.disconnect(session_id)
                await websocket.close(code=1003)

    except WebSocketDisconnect:
        ws_manager.disconnect(session_id)
        logger.info(f"WebSocket disconnected for session_id: {session_id}")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
