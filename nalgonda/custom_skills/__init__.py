# Mapping skill names to actual skill classes
from agency_swarm.tools import CodeInterpreter, Retrieval

from nalgonda.custom_skills.build_directory_tree import BuildDirectoryTree
from nalgonda.custom_skills.generate_proposal import GenerateProposal
from nalgonda.custom_skills.print_all_files_in_path import PrintAllFilesInPath
from nalgonda.custom_skills.print_file_contents import PrintFileContents
from nalgonda.custom_skills.save_lead_to_airtable import SaveLeadToAirtable
from nalgonda.custom_skills.search_web import SearchWeb
from nalgonda.custom_skills.summarize_all_code_in_path import SummarizeAllCodeInPath
from nalgonda.custom_skills.summarize_code import SummarizeCode
from nalgonda.custom_skills.write_and_save_program import WriteAndSaveProgram

SKILL_MAPPING = {
    "CodeInterpreter": CodeInterpreter,
    "Retrieval": Retrieval,
    "BuildDirectoryTree": BuildDirectoryTree,
    "GenerateProposal": GenerateProposal,
    "PrintAllFilesInPath": PrintAllFilesInPath,
    "PrintFileContents": PrintFileContents,
    "SaveLeadToAirtable": SaveLeadToAirtable,
    "SearchWeb": SearchWeb,
    "SummarizeAllCodeInPath": SummarizeAllCodeInPath,
    "SummarizeCode": SummarizeCode,
    "WriteAndSaveProgram": WriteAndSaveProgram,
}
