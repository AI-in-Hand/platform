import pytest

from tests.testing_utils import TEST_USER_ID


@pytest.mark.usefixtures("mock_get_current_user")
def test_get_variables(client, mock_firestore_client):
    mock_firestore_client.setup_mock_data(
        "user_variables", TEST_USER_ID, {"VARIABLE1": "value1", "VARIABLE2": "value2"}
    )
    response = client.get("/api/v1/user/settings/variables")
    assert response.status_code == 200
    assert response.json()["data"] == ["OPENAI_API_KEY", "VARIABLE1", "VARIABLE2"]


@pytest.mark.usefixtures("mock_get_current_user")
def test_update_variables(client, mock_firestore_client):
    variables = {"VARIABLE1": "value1", "VARIABLE2": "value2"}
    response = client.put("/api/v1/user/settings/variables", json=variables)
    assert response.status_code == 200
    assert response.json() == {
        "message": "Variables updated successfully",
        "status": True,
        "data": ["OPENAI_API_KEY", "VARIABLE1", "VARIABLE2"],
    }
    updated_variables = mock_firestore_client.to_dict()
    assert len(updated_variables) == 2
