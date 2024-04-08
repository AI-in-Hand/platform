import pytest

from tests.testing_utils import TEST_USER_ID


@pytest.mark.usefixtures("mock_get_current_user")
def test_get_secrets(client, mock_firestore_client):
    mock_firestore_client.setup_mock_data("user_secrets", TEST_USER_ID, {"SECRET1": "value1", "SECRET2": "value2"})
    response = client.get("/v1/api/user/settings/secrets")
    assert response.status_code == 200
    assert response.json()["data"] == ["OPENAI_API_KEY", "SECRET1", "SECRET2"]


@pytest.mark.usefixtures("mock_get_current_user")
def test_update_secrets(client, mock_firestore_client):
    secrets = {"SECRET1": "value1", "SECRET2": "value2"}
    response = client.put("/v1/api/user/settings/secrets", json=secrets)
    assert response.status_code == 200
    assert response.json() == {
        "message": "Secrets updated successfully",
        "status": True,
        "data": ["OPENAI_API_KEY", "SECRET1", "SECRET2"],
    }
    updated_secrets = mock_firestore_client.to_dict()
    assert len(updated_secrets) == 2
