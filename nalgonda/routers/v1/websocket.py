import asyncio
import json
import logging

from agency_swarm import Agency
from agency_swarm.messages import MessageOutput
from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from websockets.exceptions import ConnectionClosedOK

from nalgonda.dependencies.agency_manager import AgencyManager, get_agency_manager
from nalgonda.websocket_connection_manager import WebSocketConnectionManager

logger = logging.getLogger(__name__)
connection_manager = WebSocketConnectionManager()
ws_router = APIRouter(
    tags=["websocket"],
    responses={404: {"description": "Not found"}},
)


@ws_router.websocket("/ws/{agency_id}")
async def websocket_initial_endpoint(
    websocket: WebSocket,
    agency_id: str,
    agency_manager: AgencyManager = Depends(get_agency_manager),
):
    """WebSocket endpoint for initial connection."""
    await base_websocket_endpoint(websocket, agency_id, agency_manager=agency_manager)


@ws_router.websocket("/ws/{agency_id}/{thread_id}")
async def websocket_thread_endpoint(
    websocket: WebSocket,
    agency_id: str,
    thread_id: str,
    agency_manager: AgencyManager = Depends(get_agency_manager),
):
    """WebSocket endpoint for maintaining conversation with a specific thread."""
    await base_websocket_endpoint(websocket, agency_id, thread_id=thread_id, agency_manager=agency_manager)


async def base_websocket_endpoint(
    websocket: WebSocket,
    agency_id: str,
    agency_manager: AgencyManager,
    thread_id: str | None = None,
) -> None:
    """Common logic for WebSocket endpoint handling.
    Send messages to and from CEO of the given agency."""

    # TODO: Add authentication: check if agency_id is valid for the given user

    await connection_manager.connect(websocket)
    logger.info(f"WebSocket connected for agency_id: {agency_id}, thread_id: {thread_id}")

    agency = await agency_manager.get_agency(agency_id, thread_id)
    if not agency:
        # TODO: remove this once Redis is used for storing agencies:
        # the problem now is that cache is empty in the websocket thread
        agency, _ = await agency_manager.create_agency(agency_id)
        # await connection_manager.send_message("Agency not found", websocket)
        # await connection_manager.disconnect(websocket)
        # await websocket.close()
        # return

    try:
        await websocket_receive_and_process_messages(websocket, agency_id, agency, thread_id, agency_manager)
    except (WebSocketDisconnect, ConnectionClosedOK):
        await connection_manager.disconnect(websocket)
        logger.info(f"WebSocket disconnected for agency_id: {agency_id}")


async def websocket_receive_and_process_messages(
    websocket: WebSocket,
    agency_id: str,
    agency: Agency,
    thread_id: str | None,
    agency_manager: AgencyManager,
) -> None:
    """Receive messages from the websocket and process them."""
    while True:
        try:
            user_message = await websocket.receive_text()

            if not user_message.strip():
                await connection_manager.send_message("message not provided", websocket)
                continue

            await process_ws_message(user_message, agency, websocket)

            new_thread_id = await agency_manager.refresh_thread_id(agency, agency_id, thread_id)
            if new_thread_id is not None:
                logger.info(f"Thread ID changed from {thread_id} to {new_thread_id}")
                await connection_manager.send_message(json.dumps({"thread_id": new_thread_id}), websocket)
                thread_id = new_thread_id

        except (WebSocketDisconnect, ConnectionClosedOK) as e:
            raise e
        except Exception:
            logger.exception(f"Exception while processing message: agency_id: {agency_id}, thread_id: {thread_id}")
            await connection_manager.send_message("Something went wrong. Please try again.", websocket)
            continue


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
        await connection_manager.send_message(response_text, websocket)
