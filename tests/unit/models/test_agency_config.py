import pytest

from backend.models.agency_config import AgencyConfig


def test_empty_agency_chart():
    # Test should pass with an empty agency chart
    config = AgencyConfig(id="123", name="Test agency", agents=["Agent1", "Agent2"], agency_chart={}, main_agent="CEO")
    assert config.agency_chart == {}


def test_invalid_list_size_in_agency_chart():
    # Test should fail if any list element in the agency chart does not contain exactly 2 strings
    with pytest.raises(ValueError) as excinfo:
        AgencyConfig(
            id="123",
            name="Test agency",
            agents=["Agent1", "Agent2", "Agent3"],
            main_agent="CEO",
            agency_chart={"0": ["CEO"]},
        )
    assert "List should have at least 2 items after validation" in str(excinfo.value)


def test_main_agent_not_in_agency_chart():
    # Test should fail if the main_agent is not included in the agency chart
    with pytest.raises(ValueError) as excinfo:
        AgencyConfig(
            id="123",
            name="Test agency",
            agents=["Agent1", "Agent2"],
            main_agent="CEO",
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
            main_agent="CEO",
            agency_chart={"0": ["CEO", "CEO"]},
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
    assert "Value error, Please add at least one agent" in str(excinfo.value)
