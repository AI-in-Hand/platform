import logging
import time

from agency_swarm import Agency, Agent
from agency_swarm.util.oai import get_openai_client

from base_agency.prompts import agency_manifesto, ceo_instructions, dev_instructions, va_instructions
from custom_tools.execute_command import ExecuteCommand
from custom_tools.generate_proposal import GenerateProposal
from custom_tools.search_web import SearchWeb
from custom_tools.write_and_save_program import WriteAndSaveProgram

client = get_openai_client()

logger = logging.getLogger(__name__)


class AgencyManager:
    def __init__(self):
        self.active_agencies = {}  # session_id: agency

    def get_agency(self, session_id: str) -> Agency:
        """Get the agency for the given session ID"""
        if session_id in self.active_agencies:
            return self.active_agencies[session_id]

    def create_agency(self, session_id: str) -> Agency:
        """Create the agency for the given session ID"""

        start = time.time()

        # TODO: dynamically create agents based on current settings (session_id)
        ceo = Agent(
            name=f"CEO_{session_id}",
            description="Responsible for client communication, task planning and management.",
            instructions=ceo_instructions,
            files_folder=None,  # can be a file like ./instructions.md
            tools=[],
        )

        va = Agent(
            name=f"Virtual Assistant_{session_id}",
            description="Responsible for drafting emails, doing research and writing proposals."
            "Can also search the web for information.",
            instructions=va_instructions,
            files_folder=None,
            tools=[SearchWeb, GenerateProposal],
        )

        dev = Agent(
            name=f"Developer_{session_id}",
            description="Responsible for running and executing Python Programs. Can also save programs to files, "
            "and search the web for information.",
            instructions=dev_instructions,
            files_folder=None,
            tools=[ExecuteCommand, WriteAndSaveProgram, SearchWeb],
        )

        agency_chart = [ceo, [ceo, dev], [ceo, va], [dev, va]]
        agency = Agency(agency_chart, shared_instructions=agency_manifesto)

        # measure the time it takes to create the agency
        end = time.time()
        logger.info(f"Agency creation took {end - start} seconds. Session ID: {session_id}")

        self.active_agencies[session_id] = agency
        return agency


if __name__ == "__main__":
    agency_manager = AgencyManager()
    agency_1 = agency_manager.create_agency("test")
    agency_2 = agency_manager.get_agency("test")
    assert agency_1 == agency_2

    agency_1.run_demo()
