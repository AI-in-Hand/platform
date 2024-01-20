import sys
from unittest.mock import MagicMock, Mock, patch

import pytest

from tests.test_utils.mock_firestore_client import MockFirestoreClient

sys.modules["agency_swarm.util.oai"] = Mock()


@pytest.fixture(autouse=True)
def mock_firestore_client():
    firestore_client = MockFirestoreClient()
    with patch("firebase_admin.firestore.client", return_value=firestore_client):
        yield firestore_client


@pytest.fixture(autouse=True)
def mock_init_oai():
    with patch("agency_swarm.Agent.init_oai"):
        yield


tool1 = MagicMock()
tool2 = MagicMock()
tool1.__name__ = "tool1"
tool2.__name__ = "tool2"
MOCK_TOOL_MAPPING = {"tool1": tool1, "tool2": tool2}


@pytest.fixture(autouse=True)
def mock_tool_mapping():
    with patch("nalgonda.services.agent_manager.TOOL_MAPPING", MOCK_TOOL_MAPPING):
        yield
