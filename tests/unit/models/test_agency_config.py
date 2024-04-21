import pytest
from pydantic import ValidationError

from backend.models.agency_config import AgencyConfig, AgencyConfigForAPI, CommunicationFlow
from backend.models.agent_flow_spec import AgentFlowSpecForAPI


def test_empty_agency_chart():
    # Test should pass with an empty agency chart
    config = AgencyConfig(
        id="123", name="Test agency", agents=["Agent1", "Agent2"], agency_chart={}, main_agent="Agent1"
    )
    assert config.agency_chart == {}


def test_invalid_list_size_in_agency_chart():
    # Test should fail if any list element in the agency chart does not contain exactly 2 strings
    with pytest.raises(ValueError) as excinfo:
        AgencyConfig(
            id="123",
            name="Test agency",
            agents=["Agent1", "Agent2", "Agent3"],
            main_agent="Agent1",
            agency_chart={"0": ["Agent1"]},
        )
    assert "List should have at least 2 items after validation" in str(excinfo.value)


def test_main_agent_not_in_agency_chart():
    # Test should fail if the main_agent is not included in the agency chart
    with pytest.raises(ValueError) as excinfo:
        AgencyConfig(
            id="123",
            name="Test agency",
            agents=["Agent1", "Agent2"],
            main_agent="Agent3",
            agency_chart={"0": ["Agent1", "Agent2"]},
        )
    assert "The main agent must be in the agency chart" in str(excinfo.value)


def test_duplicate_agents_in_agency_chart():
    # Test should fail if the agency chart row contains duplicate agents
    with pytest.raises(ValueError) as excinfo:
        AgencyConfig(
            id="123",
            name="Test agency",
            agents=["Agent1", "Agent2"],
            main_agent="Agent1",
            agency_chart={"0": ["Agent1", "Agent1"]},
        )
    assert "Chart row must be unique" in str(excinfo.value)


def test_main_agent_not_set():
    with pytest.raises(ValueError) as excinfo:
        AgencyConfig(
            id="123",
            name="Test agency",
            agents=["Agent1", "Agent2"],
            agency_chart={"0": ["Agent1", "Agent2"]},
            main_agent=None,
        )
    assert "Please add at least one agent" in str(excinfo.value)


def test_empty_flows_in_agency_config_for_api():
    # Test should fail if the flows list is empty
    with pytest.raises(ValueError) as excinfo:
        AgencyConfigForAPI(
            id="123",
            name="Test agency",
            flows=[],
        )
    assert "Please add at least one agent" in str(excinfo.value)


def test_missing_sender_in_communication_flow():
    # Test should fail if a communication flow is missing a sender
    with pytest.raises(ValidationError) as excinfo:
        AgencyConfigForAPI(
            id="123",
            name="Test agency",
            flows=[CommunicationFlow(sender=None, receiver=AgentFlowSpecForAPI(config={"name": "Agent1"}))],
        )
    assert "Sender agent is required" in str(excinfo.value)


def test_missing_receiver_in_multiple_communication_flows():
    # Test should fail if there are multiple communication flows and any flow is missing a receiver
    with pytest.raises(ValidationError) as excinfo:
        AgencyConfigForAPI(
            id="123",
            name="Test agency",
            flows=[
                CommunicationFlow(
                    sender=AgentFlowSpecForAPI(config={"name": "Agent1"}),
                    receiver=AgentFlowSpecForAPI(config={"name": "Agent2"}),
                ),
                CommunicationFlow(sender=AgentFlowSpecForAPI(config={"name": "Agent3"}), receiver=None),
            ],
        )
    assert "Receiver agent is required" in str(excinfo.value)


def test_valid_agency_config_for_api():
    # Test should pass with valid communication flows
    config = AgencyConfigForAPI(
        id="123",
        name="Test agency",
        flows=[
            CommunicationFlow(
                sender=AgentFlowSpecForAPI(config={"name": "Agent1"}),
                receiver=AgentFlowSpecForAPI(config={"name": "Agent1"}),
            ),
            CommunicationFlow(
                sender=AgentFlowSpecForAPI(config={"name": "Agent2"}),
                receiver=AgentFlowSpecForAPI(config={"name": "Agent2"}),
            ),
        ],
    )
    assert len(config.flows) == 2
