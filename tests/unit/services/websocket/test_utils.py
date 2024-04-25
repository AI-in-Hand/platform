from unittest.mock import MagicMock

from agency_swarm.messages import MessageOutput

from backend.services.context_vars_manager import ContextEnvVarsManager
from backend.services.websocket.utils import get_next_response


def test_get_next_response_with_response():
    user_id = "user_id"
    agency_id = "agency_id"
    response = MagicMock(spec=MessageOutput)

    def response_generator():
        yield response

    result = get_next_response(response_generator(), user_id, agency_id)

    assert result == response
    assert ContextEnvVarsManager.get("user_id") == user_id
    assert ContextEnvVarsManager.get("agency_id") == agency_id


def test_get_next_response_no_response():
    user_id = "user_id"
    agency_id = "agency_id"

    def response_generator():
        yield from []

    result = get_next_response(response_generator(), user_id, agency_id)

    assert result is None
    assert ContextEnvVarsManager.get("user_id") == user_id
    assert ContextEnvVarsManager.get("agency_id") == agency_id
