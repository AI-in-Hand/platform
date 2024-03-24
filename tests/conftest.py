import sys
from unittest.mock import MagicMock, patch

import pytest

from nalgonda.settings import settings
from tests.test_utils.constants import TEST_ENCRYPTION_KEY
from tests.test_utils.mock_firestore_client import MockFirestoreClient

oai_mock = MagicMock(get_openai_client=MagicMock(return_value=MagicMock(timeout=10)))
sys.modules["agency_swarm.util.oai"] = oai_mock
settings.encryption_key = TEST_ENCRYPTION_KEY


@pytest.fixture(autouse=True)
def mock_firestore_client():
    firestore_client = MockFirestoreClient()
    with patch("firebase_admin.firestore.client", return_value=firestore_client):
        yield firestore_client


@pytest.fixture()
def recover_oai_client():
    from . import oai_mock, original_oai_client

    sys.modules["nalgonda.services.oai_client"] = original_oai_client
    yield
    sys.modules["nalgonda.services.oai_client"] = oai_mock


@pytest.fixture(autouse=True)
def mock_init_oai():
    with patch("agency_swarm.Agent.init_oai") as mock:
        yield mock


skill1 = MagicMock()
skill2 = MagicMock()
skill1.__name__ = "skill1"
skill2.__name__ = "skill2"
MOCK_SKILL_MAPPING = {"skill1": skill1, "skill2": skill2}


@pytest.fixture(autouse=True)
def mock_skill_mapping():
    with patch("nalgonda.services.agent_manager.SKILL_MAPPING", MOCK_SKILL_MAPPING):
        yield


@pytest.fixture
def mock_setup_logging():
    with patch("nalgonda.utils.logging_utils.setup_logging"):
        yield
