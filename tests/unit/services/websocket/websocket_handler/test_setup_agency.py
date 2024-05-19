from unittest.mock import MagicMock

import pytest

from backend.exceptions import NotFoundError
from backend.models.session_config import SessionConfig


@pytest.mark.asyncio
async def test_setup_agency(websocket_handler):
    user_id = "user_id"
    session_id = "session_id"
    session = SessionConfig(
        id="session_id",
        name="Session",
        user_id=user_id,
        agency_id="agency_id",
        thread_ids={"thread1": "thread1", "thread2": "thread2"},
    )
    agency = MagicMock()

    websocket_handler.session_manager.get_session.return_value = session
    websocket_handler.agency_manager.get_agency.return_value = (agency, None)

    result_session, result_agency = await websocket_handler._setup_agency(user_id, session_id)

    assert result_session == session
    assert result_agency == agency
    websocket_handler.session_manager.get_session.assert_called_once_with(session_id)
    websocket_handler.agency_manager.get_agency.assert_awaited_once_with(session.agency_id, session.thread_ids, user_id)


@pytest.mark.asyncio
async def test_setup_agency_session_not_found(websocket_handler):
    user_id = "user_id"
    session_id = "session_id"

    websocket_handler.session_manager.get_session.side_effect = NotFoundError("Session", session_id)

    with pytest.raises(NotFoundError, match="Session not found: session_id"):
        await websocket_handler._setup_agency(user_id, session_id)
