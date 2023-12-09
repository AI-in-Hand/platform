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
        self.cache = {}  # agency_id: agency

    async def get_or_create_agency(self, agency_id: str) -> Agency:
        """Get or create the agency for the given session ID"""
        if agency_id in self.cache:
            return self.cache[agency_id]

        start = asyncio.get_event_loop().time()
        agency = await asyncio.to_thread(self.load_agency_from_config, agency_id)
        end = asyncio.get_event_loop().time()
        logger.info(f"Agency creation took {end - start} seconds. Session ID: {agency_id}")

        self.cache[agency_id] = agency
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
    agency_1 = asyncio.run(agency_manager.get_or_create_agency("test"))
    agency_1.run_demo()
