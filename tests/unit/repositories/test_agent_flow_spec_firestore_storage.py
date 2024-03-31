import pytest

from backend.models.agent_flow_spec import AgentFlowSpec
from backend.repositories.agent_flow_spec_firestore_storage import AgentFlowSpecFirestoreStorage
from tests.test_utils import TEST_USER_ID


@pytest.fixture
def agent_data():
    return {
        "id": "agent1",
        "type": "userproxy",
        "config": {
            "name": "example_name",
            "system_message": "Do something important",
            "code_execution_config": {
                "work_dir": "test_agency_dir",
                "use_docker": False,
            },
        },
        "timestamp": "2021-09-01T00:00:00",
        "skills": ["skill1", "skill2"],
        "description": "An example agent",
        "user_id": TEST_USER_ID,
    }


def test_load_agent_flow_spec(mock_firestore_client, agent_data):
    # Setup mock data
    # setup_mock_data(collection_name, document_name, data)
    mock_firestore_client.setup_mock_data("agent_configs", "agent1", agent_data)

    storage = AgentFlowSpecFirestoreStorage()
    loaded_agent_flow_spec = storage.load_by_id(agent_data["id"])

    expected_agent_flow_spec = AgentFlowSpec.model_validate(agent_data)
    assert loaded_agent_flow_spec == expected_agent_flow_spec


def test_save_existing_agent_flow_spec(mock_firestore_client, agent_data):
    mock_firestore_client.setup_mock_data("agent_configs", "agent1", agent_data)

    agent_flow_spec = AgentFlowSpec(**agent_data)
    storage = AgentFlowSpecFirestoreStorage()
    storage.save(agent_flow_spec)

    serialized_data = agent_flow_spec.model_dump()
    assert mock_firestore_client.to_dict() == serialized_data


def test_save_new_agent_flow_spec(mock_firestore_client, agent_data):
    mock_firestore_client.setup_mock_data("agent_configs", "new_agent_id", agent_data, doc_id="new_agent_id")

    new_agent_data = agent_data.copy()
    # Remove agent id to simulate a new agent
    del new_agent_data["id"]
    agent_flow_spec = AgentFlowSpec(**new_agent_data)

    storage = AgentFlowSpecFirestoreStorage()
    storage.save(agent_flow_spec)

    serialized_data = agent_flow_spec.model_dump()
    assert mock_firestore_client.to_dict() == serialized_data
    # Check that the agent id was updated
    assert agent_flow_spec.id == "new_agent_id"
