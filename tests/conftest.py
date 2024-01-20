from unittest.mock import patch

import pytest

from tests.test_utils.mock_firestore_client import MockFirestoreClient


@pytest.fixture(autouse=True)
def mock_firestore_client():
    firestore_client = MockFirestoreClient()
    with patch("firebase_admin.firestore.client", return_value=firestore_client):
        yield firestore_client
