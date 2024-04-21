import pytest

from backend.models.agency_config import AgencyConfig, AgencyConfigForAPI, CommunicationFlow
from backend.models.agent_flow_spec import AgentConfig, AgentFlowSpec, AgentFlowSpecForAPI
from backend.repositories.agent_flow_spec_storage import AgentFlowSpecStorage
from backend.services.adapters.agency_adapter import AgencyAdapter


@pytest.fixture
def agent_flow_spec_storage() -> AgentFlowSpecStorage:
    return AgentFlowSpecStorage()


@pytest.fixture
def agency_adapter(agent_flow_spec_storage, agent_adapter) -> AgencyAdapter:
    return AgencyAdapter(agent_flow_spec_storage, agent_adapter)


def test_to_model(agency_adapter):
    sender = AgentFlowSpecForAPI(id="sender_id", config=AgentConfig(name="Sender"))
    receiver = AgentFlowSpecForAPI(id="receiver_id", config=AgentConfig(name="Receiver"))
    agency_config_api = AgencyConfigForAPI(
        id="agency_id",
        name="Test Agency",
        description="Test Description",
        shared_instructions="Test Instructions",
        flows=[
            CommunicationFlow(sender=sender, receiver=receiver),
            CommunicationFlow(sender=sender),
        ],
    )
    agency_config = agency_adapter.to_model(agency_config_api)
    assert agency_config.name == "Test Agency"
    assert agency_config.description == "Test Description"
    assert agency_config.shared_instructions == "Test Instructions"
    assert set(agency_config.agents) == {"sender_id", "receiver_id"}
    assert agency_config.main_agent == "Sender"
    assert agency_config.agency_chart == {
        "0": ["Sender", "Receiver"],
        "1": ["Sender", None],
    }


def test_to_api(agency_adapter, agent_adapter, mocker):
    sender = AgentFlowSpec(id="sender_id", config=AgentConfig(name="Sender"))
    receiver = AgentFlowSpec(id="receiver_id", config=AgentConfig(name="Receiver"))
    agency_config = AgencyConfig(
        id="agency_id",
        name="Test Agency",
        description="Test Description",
        shared_instructions="Test Instructions",
        agents=["sender_id", "receiver_id"],
        main_agent="Sender",
        agency_chart={
            "0": ["Sender", "Receiver"],
            "1": ["Sender", None],
        },
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
    assert len(agency_config_api.flows) == 2
    assert agency_config_api.flows[0].sender == agent_adapter.to_api(sender)
    assert agency_config_api.flows[0].receiver == agent_adapter.to_api(receiver)
    assert agency_config_api.flows[1].sender == agent_adapter.to_api(sender)
    assert agency_config_api.flows[1].receiver is None


def test_to_api_without_agents(agency_adapter):
    agency_config = AgencyConfig(
        id="agency_id",
        name="Test Agency",
        description="Test Description",
        shared_instructions="Test Instructions",
        agents=[],
        main_agent=None,
        agency_chart={},
    )
    agency_config_api = agency_adapter.to_api(agency_config)
    assert agency_config_api.name == "Test Agency"
    assert agency_config_api.description == "Test Description"
    assert agency_config_api.shared_instructions == "Test Instructions"
    assert agency_config_api.flows == []
