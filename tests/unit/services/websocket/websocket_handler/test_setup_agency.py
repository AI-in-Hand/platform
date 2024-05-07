import pytest

from backend.exceptions import NotFoundError


@pytest.mark.asyncio
async def test_setup_agency_session_not_found(websocket_handler):
    agency_id = "agency_id"
    user_id = "user_id"
    session_id = "session_id"

    websocket_handler.session_manager.get_session.side_effect = NotFoundError("Session", session_id)

    with pytest.raises(NotFoundError, match="Session not found: session_id"):
        await websocket_handler._setup_agency(agency_id, user_id, session_id)
