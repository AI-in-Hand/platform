from unittest.mock import MagicMock

from agency_swarm.messages import MessageOutput

from backend.services.context_vars_manager import ContextEnvVarsManager
from backend.services.websocket.utils import get_next_response


def test_get_next_response_with_response():
    agency = MagicMock()
    user_message = "User message"
    user_id = "user_id"
    agency_id = "agency_id"
    response = MagicMock(spec=MessageOutput)
    agency.get_completion.return_value = iter([response])

    result = get_next_response(agency, user_message, user_id, agency_id)

    assert result == response
    agency.get_completion.assert_called_once_with(message=user_message, yield_messages=True)
    assert ContextEnvVarsManager.get("user_id") == user_id
    assert ContextEnvVarsManager.get("agency_id") == agency_id


def test_get_next_response_no_response():
    agency = MagicMock()
    user_message = "User message"
    user_id = "user_id"
    agency_id = "agency_id"
    agency.get_completion.return_value = iter([])

    result = get_next_response(agency, user_message, user_id, agency_id)

    assert result is None
    agency.get_completion.assert_called_once_with(message=user_message, yield_messages=True)
    assert ContextEnvVarsManager.get("user_id") == user_id
    assert ContextEnvVarsManager.get("agency_id") == agency_id
