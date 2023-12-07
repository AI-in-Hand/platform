# Mapping tool names to actual tool classes
from custom_tools.execute_command import ExecuteCommand
from custom_tools.generate_proposal import GenerateProposal
from custom_tools.search_web import SearchWeb
from custom_tools.write_and_save_program import WriteAndSaveProgram

TOOL_MAPPING = {
    "SearchWeb": SearchWeb,
    "GenerateProposal": GenerateProposal,
    "ExecuteCommand": ExecuteCommand,
    "WriteAndSaveProgram": WriteAndSaveProgram,
}
