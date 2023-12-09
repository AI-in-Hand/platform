# Mapping tool names to actual tool classes
from agency_swarm.tools import CodeInterpreter, Retrieval

from custom_tools.build_directory_tree import BuildDirectoryTree
from custom_tools.generate_proposal import GenerateProposal
from custom_tools.print_all_files_in_directory import PrintAllFilesInDirectory
from custom_tools.search_web import SearchWeb
from custom_tools.write_and_save_program import WriteAndSaveProgram

TOOL_MAPPING = {
    "CodeInterpreter": CodeInterpreter,
    "Retrieval": Retrieval,
    "BuildDirectoryTree": BuildDirectoryTree,
    "GenerateProposal": GenerateProposal,
    "PrintAllFilesInDirectory": PrintAllFilesInDirectory,
    "SearchWeb": SearchWeb,
    "WriteAndSaveProgram": WriteAndSaveProgram,
}
