import pytest

from tests.testing_utils import TEST_USER_ID
from tests.testing_utils.constants import TEST_AGENCY_ID


@pytest.fixture
def session_config_data():
    return {
        "id": "test_session_id",
        "name": "Test agency",
        "user_id": TEST_USER_ID,
        "agency_id": TEST_AGENCY_ID,
        "thread_ids": {},
        "timestamp": "2021-10-01T00:00:00Z",
    }
