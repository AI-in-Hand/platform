import pytest

from backend.models.agency_config import AgencyConfig, AgencyConfigForAPI
from backend.models.agent_flow_spec import AgentConfig, AgentFlowSpec
from backend.repositories.agent_flow_spec_firestore_storage import AgentFlowSpecFirestoreStorage
from backend.services.adapters.agency_adapter import AgencyConfigAdapter


@pytest.fixture
def agent_flow_spec_storage():
    return AgentFlowSpecFirestoreStorage()


@pytest.fixture
def agency_adapter(agent_flow_spec_storage):
    return AgencyConfigAdapter(agent_flow_spec_storage)


def test_to_model(agency_adapter):
    sender = AgentFlowSpec(id="sender_id", config=AgentConfig(name="Sender"))
    receiver = AgentFlowSpec(id="receiver_id", config=AgentConfig(name="Receiver"))
    agency_config_api = AgencyConfigForAPI(
        name="Test Agency",
        description="Test Description",
        shared_instructions="Test Instructions",
        sender=sender,
        receiver=receiver,
    )

    agency_config = agency_adapter.to_model(agency_config_api)

    assert agency_config.name == "Test Agency"
    assert agency_config.description == "Test Description"
    assert agency_config.shared_instructions == "Test Instructions"
    assert agency_config.agents == ["sender_id", "receiver_id"]
    assert agency_config.main_agent == "Sender"
    assert agency_config.agency_chart == [["Sender", "Receiver"]]


def test_to_model_without_receiver(agency_adapter):
    sender = AgentFlowSpec(id="sender_id", config=AgentConfig(name="Sender"))
    agency_config_api = AgencyConfigForAPI(
        name="Test Agency",
        description="Test Description",
        shared_instructions="Test Instructions",
        sender=sender,
    )

    agency_config = agency_adapter.to_model(agency_config_api)

    assert agency_config.name == "Test Agency"
    assert agency_config.description == "Test Description"
    assert agency_config.shared_instructions == "Test Instructions"
    assert agency_config.agents == ["sender_id"]
    assert agency_config.main_agent == "Sender"
    assert agency_config.agency_chart == []


def test_to_api(agency_adapter, mocker):
    sender = AgentFlowSpec(id="sender_id", config=AgentConfig(name="Sender"))
    receiver = AgentFlowSpec(id="receiver_id", config=AgentConfig(name="Receiver"))
    agency_config = AgencyConfig(
        name="Test Agency",
        description="Test Description",
        shared_instructions="Test Instructions",
        agents=["sender_id", "receiver_id"],
        main_agent="Sender",
        agency_chart=[["Sender", "Receiver"]],
    )

    mocker.patch.object(
        agency_adapter.agent_flow_spec_storage,
        "load_by_ids",
        return_value=[sender, receiver],
    )

    agency_config_api = agency_adapter.to_api(agency_config)

    assert agency_config_api.name == "Test Agency"
    assert agency_config_api.description == "Test Description"
    assert agency_config_api.shared_instructions == "Test Instructions"
    assert agency_config_api.sender == sender
    assert agency_config_api.receiver == receiver


def test_to_api_without_receiver(agency_adapter, mocker):
    sender = AgentFlowSpec(id="sender_id", config=AgentConfig(name="Sender"))
    agency_config = AgencyConfig(
        name="Test Agency",
        description="Test Description",
        shared_instructions="Test Instructions",
        agents=["sender_id"],
        main_agent="Sender",
        agency_chart=[],
    )

    mocker.patch.object(
        agency_adapter.agent_flow_spec_storage,
        "load_by_ids",
        return_value=[sender],
    )

    agency_config_api = agency_adapter.to_api(agency_config)

    assert agency_config_api.name == "Test Agency"
    assert agency_config_api.description == "Test Description"
    assert agency_config_api.shared_instructions == "Test Instructions"
    assert agency_config_api.sender == sender
    assert agency_config_api.receiver is None
