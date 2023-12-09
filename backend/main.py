import asyncio
import logging
import uuid

from fastapi import FastAPI, WebSocket, WebSocketDisconnect

from agency_manager import AgencyManager
from constants import DATA_DIR

# Ensure directories exist
DATA_DIR.mkdir(exist_ok=True)

app = FastAPI()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        # logging.FileHandler(DATA_DIR / "logs.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)

agency_manager = AgencyManager()


@app.post("/create_agency")
async def create_agency():
    """Create a new agency and return its id."""

    # TODO: Add authentication: check if user is logged in and has permission to create an agency
    agency_id = uuid.uuid4().hex
    await agency_manager.get_or_create_agency(agency_id)
    return {"agency_id": agency_id}


class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)


ws_manager = ConnectionManager()


@app.websocket("/ws/{agency_id}")
async def websocket_endpoint(websocket: WebSocket, agency_id: str):
    """Send messages to and from CEO of the given agency."""

    # TODO: Add authentication: check if agency_id is valid for the given user

    await ws_manager.connect(websocket)
    logger.info(f"WebSocket connected for agency_id: {agency_id}")

    agency = await agency_manager.get_or_create_agency(agency_id=agency_id)

    try:
        while True:
            user_message = await websocket.receive_text()

            if not user_message.strip():
                await ws_manager.send_message("message not provided", websocket)
                ws_manager.disconnect(websocket)
                await websocket.close(code=1003)
                return

            gen = await asyncio.to_thread(agency.get_completion, message=user_message, yield_messages=True)
            for response in gen:
                response_text = response.get_formatted_content()
                await ws_manager.send_message(response_text, websocket)

    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)
        logger.info(f"WebSocket disconnected for agency_id: {agency_id}")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
