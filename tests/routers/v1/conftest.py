from unittest.mock import MagicMock

import pytest


@pytest.fixture
def mock_agent_manager():
    mock_manager = MagicMock()
    mock_manager.create_or_update_agent = MagicMock(return_value="test_agent_id")
    return mock_manager
