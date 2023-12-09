import asyncio
import logging

from agency_swarm import Agency, Agent
from agency_swarm.util.oai import get_openai_client

from config import AgencyConfig
from custom_tools import TOOL_MAPPING

client = get_openai_client()

logger = logging.getLogger(__name__)


class AgencyManager:
    def __init__(self):
        self.active_agencies = {}  # agency_id: agency

    def get_agency(self, agency_id: str) -> Agency | None:
        """Get the agency for the given session ID"""
        if agency_id in self.active_agencies:
            return self.active_agencies[agency_id]
        return None

    async def create_agency(self, agency_id: str) -> Agency:
        """Create the agency for the given session ID"""
        start = asyncio.get_event_loop().time()

        agency = await asyncio.to_thread(self.load_agency_from_config, agency_id)
        self.active_agencies[agency_id] = agency

        end = asyncio.get_event_loop().time()
        logger.info(f"Agency creation took {end - start} seconds. Session ID: {agency_id}")
        return agency

    @classmethod
    def load_agency_from_config(cls, agency_id: str) -> Agency:
        """Load the agency from the config file"""

        config = AgencyConfig.load(agency_id)

        agents = {
            agent_conf.role: Agent(
                id=agent_conf.id,
                name=f"{agent_conf.role}_{agency_id}",
                description=agent_conf.description,
                instructions=agent_conf.instructions,
                files_folder=agent_conf.files_folder,
                tools=[TOOL_MAPPING[tool] for tool in agent_conf.tools if tool in TOOL_MAPPING],
            )
            for agent_conf in config.agents
        }

        # Create agency chart based on the config
        agency_chart = [
            [agents[role] for role in chart] if isinstance(chart, list) else agents[chart]
            for chart in config.agency_chart
        ]

        agency = Agency(agency_chart, shared_instructions=config.agency_manifesto)

        config.update_agent_ids_in_config(agency_id, agents=agency.agents)

        config.save(agency_id)

        return agency


if __name__ == "__main__":
    # Test the agency manager
    agency_manager = AgencyManager()
    agency_1 = asyncio.run(agency_manager.create_agency("test"))
    agency_2 = agency_manager.get_agency("test")
    assert agency_1 == agency_2

    agency_1.run_demo()
