import time

from agency_swarm import Agency, Agent
from agency_swarm.util.oai import get_openai_client

from base_agency.prompts import agency_manifesto, ceo_instructions, dev_instructions, va_instructions
from custom_tools.execute_command import ExecuteCommand
from custom_tools.generate_proposal import GenerateProposal
from custom_tools.search_web import SearchWeb
from custom_tools.write_and_save_program import WriteAndSaveProgram

client = get_openai_client()

# TODO: make this a database
agencies = {}


def get_agency(session_id: str) -> Agency:
    """Get the agency for the given session ID"""
    if session_id in agencies:
        return agencies[session_id]
    agency = create_agency(session_id)
    agencies[session_id] = agency
    return agency


def create_agency(session_id: str) -> Agency:
    """Create the agency for the given session ID"""

    start = time.time()

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
        description="Responsible for running and executing Python Programs. Can also save programs to files.",
        instructions=dev_instructions,
        files_folder=None,
        tools=[ExecuteCommand, WriteAndSaveProgram],
    )

    agency = Agency([ceo, [ceo, dev], [ceo, va], [dev, va]], shared_instructions=agency_manifesto)

    # measure the time it takes to create the agency
    end = time.time()
    print(f"Agency creation took {end - start} seconds")

    agencies[session_id] = agency
    return agency


if __name__ == "__main__":
    agency = get_agency("test")
    agency.run_demo()
