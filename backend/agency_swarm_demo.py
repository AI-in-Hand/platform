from getpass import getpass

from agency_swarm import Agency, Agent, set_openai_key
from agency_swarm.util.oai import get_openai_client

from custom_tools.execute_command import ExecuteCommand
from custom_tools.generate_proposal import GenerateProposal
from custom_tools.search_web import SearchWeb
from custom_tools.write_and_save_program import WriteAndSaveProgram

set_openai_key(getpass("Please enter your openai key: "))
client = get_openai_client()


ceo_instructions = """# Instructions for CEO Agent

- Ensure that proposal is send to the user before proceeding with task execution.
- Delegate tasks to appropriate agents, ensuring they align with their expertise and capabilities.
- Clearly define the objectives and expected outcomes for each task.
- Provide necessary context and background information for successful task completion.
- Maintain ongoing communication with agents until complete task execution.
- Review completed tasks to ensure they meet the set objectives.
- Report the results back to the user."""

ceo = Agent(
    name="CEO",
    description="Responsible for client communication, task planning and management.",
    instructions=ceo_instructions,  # can be a file like ./instructions.md
    files_folder=None,
    tools=[],
)

"""### Custom tools"""

va_instructions = """### Instructions for Virtual Assistant

Your role is to assist users in executing tasks like below. \
If the task is outside of your capabilities, please report back to the user.

#### 1. Drafting Emails
   - **Understand Context and Tone**: Familiarize yourself with the context of each email. \
   Maintain a professional and courteous tone.
   - **Accuracy and Clarity**: Ensure that the information is accurate and presented clearly. \
   Avoid jargon unless it's appropriate for the recipient.

#### 2. Generating Proposals
   - **Gather Requirements**: Collect all necessary information about the project, \
   including client needs, objectives, and any specific requests.

#### 3. Conducting Research
   - **Understand the Objective**: Clarify the purpose and objectives of the research to focus on relevant information.
   - **Summarize Findings**: Provide clear, concise summaries of the research findings, \
   highlighting key points and how they relate to the project or inquiry.
   - **Cite Sources**: Properly cite all sources to maintain integrity and avoid plagiarism.
"""

va = Agent(
    name="Virtual Assistant",
    description="Responsible for drafting emails, doing research and writing proposals."
    "Can also search the web for information.",
    instructions=va_instructions,
    files_folder=None,
    tools=[SearchWeb, GenerateProposal],
)


dev_instructions = """# Instructions for AI Developer Agent

- Write clean and efficient Python code.
- Structure your code logically, with `main.py` as the entry point.
- Ensure correct imports according to program structure.
- Execute your code to test for functionality and errors, before reporting back to the user.
- Anticipate and handle potential runtime errors.
- Provide clear error messages for easier troubleshooting.
- Debug any issues before reporting the results back to the user.
- Always update all local files after each change, don't bother the CEO with details or code diff."""

dev = Agent(
    name="Developer",
    description="Responsible for running and executing Python Programs. Can also save programs to files.",
    instructions=dev_instructions,
    files_folder=None,
    tools=[ExecuteCommand, WriteAndSaveProgram],
)

agency_manifesto = """# "BONKIT AI" Agency Manifesto
You are a part of a virtual AI development agency called "BONKIT AI"
Your mission is to empower businesses to navigate the AI revolution successfully."""

agency = Agency([ceo, [ceo, dev], [ceo, va], [dev, va]], shared_instructions=agency_manifesto)


if __name__ == "__main__":
    agency.run_demo()
