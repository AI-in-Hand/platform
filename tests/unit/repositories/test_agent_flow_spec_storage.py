import pytest

from backend.models.agent_flow_spec import AgentFlowSpec
from backend.repositories.agent_flow_spec_storage import AgentFlowSpecStorage
from tests.testing_utils import TEST_USER_ID


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
        "timestamp": "2024-04-04T09:39:13.048457+00:00",
        "skills": ["skill1", "skill2"],
        "description": "An example agent",
        "user_id": TEST_USER_ID,
    }


@pytest.fixture
@pytest.mark.usefixtures("mock_firestore_client")
def mock_storage():
    return AgentFlowSpecStorage()


def test_load_agent_flow_spec(mock_firestore_client, agent_data):
    # Setup mock data
    # setup_mock_data(collection_name, document_name, data)
    mock_firestore_client.setup_mock_data("agent_configs", "agent1", agent_data)

    storage = AgentFlowSpecStorage()
    loaded_agent_flow_spec = storage.load_by_id(agent_data["id"])

    expected_agent_flow_spec = AgentFlowSpec.model_validate(agent_data)
    assert loaded_agent_flow_spec == expected_agent_flow_spec


def test_save_existing_agent_flow_spec(mock_firestore_client, agent_data):
    mock_firestore_client.setup_mock_data("agent_configs", "agent1", agent_data)

    agent_flow_spec = AgentFlowSpec(**agent_data)
    storage = AgentFlowSpecStorage()
    storage.save(agent_flow_spec)

    serialized_data = agent_flow_spec.model_dump()
    assert mock_firestore_client.to_dict() == serialized_data


def test_save_new_agent_flow_spec(mock_firestore_client, agent_data):
    mock_firestore_client.setup_mock_data("agent_configs", "new_agent_id", agent_data)

    new_agent_data = agent_data.copy()
    # Remove agent id to simulate a new agent
    del new_agent_data["id"]
    agent_flow_spec = AgentFlowSpec(**new_agent_data)

    storage = AgentFlowSpecStorage()
    storage.save(agent_flow_spec)

    serialized_data = agent_flow_spec.model_dump()
    assert mock_firestore_client.to_dict() == serialized_data
    # Check that the agent id was updated
    assert agent_flow_spec.id == "new_agent_id"


def test_load_agent_flow_spec_by_ids(mock_storage, mock_firestore_client, agent_data):
    # Setup multiple agents in the mock database
    ids = ["agent1", "agent2"]
    agent_data2 = agent_data.copy()
    agent_data2["id"] = "agent2"

    mock_firestore_client.setup_mock_data("agent_configs", "agent1", agent_data)
    mock_firestore_client.setup_mock_data("agent_configs", "agent2", agent_data2)

    loaded_agent_flow_specs = mock_storage.load_by_ids(ids)

    expected_agent_flow_spec1 = AgentFlowSpec.model_validate(agent_data)
    expected_agent_flow_spec2 = AgentFlowSpec.model_validate(agent_data2)

    # Assert both agents are returned and in any order
    assert len(loaded_agent_flow_specs) == 2
    assert expected_agent_flow_spec1 in loaded_agent_flow_specs
    assert expected_agent_flow_spec2 in loaded_agent_flow_specs


def test_load_agent_flow_spec_by_ids_exceeds_max_size(mock_storage):
    ids = ["agent1"] * 11

    with pytest.raises(ValueError) as excinfo:
        mock_storage._load_by_ids(ids)

    assert "IDs list exceeds the maximum size of 10 for an 'in' query in Firestore." in str(excinfo.value)


def test_delete_agent_flow_spec(mock_storage, mock_firestore_client, agent_data):
    mock_firestore_client.setup_mock_data("agent_configs", "agent1", agent_data)

    agent_flow_spec = AgentFlowSpec(**agent_data)
    mock_storage.delete(agent_flow_spec.id)

    assert mock_firestore_client.to_dict() == {}
