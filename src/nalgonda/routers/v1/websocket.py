import asyncio
import json
import logging

from agency_swarm import Agency
from agency_swarm.messages import MessageOutput
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from websockets import ConnectionClosedOK

from nalgonda.agency_manager import AgencyManager
from nalgonda.connection_manager import ConnectionManager

logger = logging.getLogger(__name__)
ws_manager = ConnectionManager()
agency_manager = AgencyManager()
ws_router = APIRouter(
    tags=["websocket"],
    responses={404: {"description": "Not found"}},
)


@ws_router.websocket("/{agency_id}/{thread_id}")
async def websocket_endpoint(websocket: WebSocket, agency_id: str, thread_id: str = "main"):
    """Send messages to and from CEO of the given agency."""

    # TODO: Add authentication: check if agency_id is valid for the given user

    await ws_manager.connect(websocket)
    logger.info(f"WebSocket connected for agency_id: {agency_id}, thread_id: {thread_id}")

    agency = await agency_manager.get_agency(agency_id, thread_id)
    if not agency:
        ws_manager.send_message("Agency not found", websocket)
        await ws_manager.disconnect(websocket)
        return

    try:
        while True:
            try:
                user_message = await websocket.receive_text()

                if not user_message.strip():
                    await ws_manager.send_message("message not provided", websocket)
                    continue

                await process_ws_message(user_message, agency, websocket)

                new_thread_id = await agency_manager.refresh_thread_id(agency, agency_id, thread_id)
                if new_thread_id is not None:
                    await ws_manager.send_message(json.dumps({"thread_id": new_thread_id}), websocket)

            except (WebSocketDisconnect, ConnectionClosedOK) as e:
                raise e
            except Exception as e:
                logger.exception(e)
                await ws_manager.send_message(f"Error: {e}\nPlease try again.", websocket)
                continue

    except WebSocketDisconnect:
        await ws_manager.disconnect(websocket)
        logger.info(f"WebSocket disconnected for agency_id: {agency_id}")
    except ConnectionClosedOK:
        logger.info(f"WebSocket disconnected for agency_id: {agency_id}")


async def process_ws_message(user_message: str, agency: Agency, websocket: WebSocket):
    """Process the user message and send the response to the websocket."""
    loop = asyncio.get_running_loop()

    gen = agency.get_completion(message=user_message, yield_messages=True)

    def get_next() -> MessageOutput | None:
        try:
            return next(gen)
        except StopIteration:
            return None

    while True:
        response = await loop.run_in_executor(None, get_next)
        if response is None:
            break

        response_text = response.get_formatted_content()
        await ws_manager.send_message(response_text, websocket)
