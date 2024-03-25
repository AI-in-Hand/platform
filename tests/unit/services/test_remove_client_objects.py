from copy import deepcopy
from unittest.mock import MagicMock

import pytest
from agency_swarm import Agency, Agent
from agency_swarm.threads import Thread

from backend.services.agency_manager import AgencyManager


@pytest.fixture
def agency():
    # Setup an Agency instance with a couple of Agents and a main_thread object
    agent1 = MagicMock(spec=Agent)
    agent1.name = "Agent1"
    agent1.client = "Client1"
    agent2 = MagicMock(spec=Agent)
    agent2.name = "Agent2"
    agent2.client = "Client2"
    main_thread = MagicMock(spec=Thread, recipient_agent=agent2)
    main_thread.client = "Client3"

    agents = [agent1, agent2]
    agency = MagicMock(spec=Agency)
    agency.name = "test_agency"
    agency.agents = agents
    agency.ceo = agent1
    agency.main_thread = main_thread
    agency.main_recipients = [agent1, agent2]
    return agency


class TestRemoveClientObjects:
    def test_remove_client_objects(self, agency):
        # Call the _remove_client_objects function
        modified_agency = AgencyManager._remove_client_objects(agency)

        # Check if all clients are set to None
        for agent in modified_agency.agents:
            assert agent.client is None

        assert modified_agency.main_thread.client is None

    def test_return_new_object(self, agency):
        # Ensure the function returns a new object, not modifying the original
        modified_agency = AgencyManager._remove_client_objects(agency)

        assert modified_agency is not agency
        assert all(
            m_agent is not o_agent for m_agent, o_agent in zip(modified_agency.agents, agency.agents, strict=True)
        )
        assert modified_agency.main_thread is not agency.main_thread

    def test_shallow_copy_behavior(self, agency):
        # Test for shallow copy behavior (non-client attributes should remain identical)
        modified_agency = AgencyManager._remove_client_objects(agency)

        # Assuming other attributes in Agency and Agent, test if they are unchanged
        # For example, if there's a 'name' attribute:
        assert modified_agency.name == agency.name
        for m_agent, o_agent in zip(modified_agency.agents, agency.agents, strict=True):
            assert m_agent.name == o_agent.name

    def test_original_object_unchanged(self, agency):
        # Create a deep copy of the original agency object for comparison
        original_agency = deepcopy(agency)

        # Call the _remove_client_objects function
        AgencyManager._remove_client_objects(agency)

        # Ensure the original object is unchanged
        for original_agent, copied_agent in zip(original_agency.agents, agency.agents, strict=True):
            assert original_agent.client is not None
            assert copied_agent.client is None

        assert original_agency.main_thread.client == agency.main_thread.client
