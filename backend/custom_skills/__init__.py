# Mapping skill names to actual skill classes
from agency_swarm.tools import CodeInterpreter, Retrieval

from backend.custom_skills.build_directory_tree import BuildDirectoryTree
from backend.custom_skills.generate_proposal import GenerateProposal
from backend.custom_skills.print_all_files_in_path import PrintAllFilesInPath
from backend.custom_skills.print_file_contents import PrintFileContents
from backend.custom_skills.save_lead_to_airtable import SaveLeadToAirtable
from backend.custom_skills.search_web import SearchWeb
from backend.custom_skills.select_from_sql_database import SelectFromSQLDatabase
from backend.custom_skills.summarize_all_code_in_path import SummarizeAllCodeInPath
from backend.custom_skills.summarize_code import SummarizeCode
from backend.custom_skills.write_and_save_program import WriteAndSaveProgram

SKILL_MAPPING = {
    "CodeInterpreter": CodeInterpreter,
    "Retrieval": Retrieval,
    "BuildDirectoryTree": BuildDirectoryTree,
    "GenerateProposal": GenerateProposal,
    "PrintAllFilesInPath": PrintAllFilesInPath,
    "PrintFileContents": PrintFileContents,
    "SaveLeadToAirtable": SaveLeadToAirtable,
    "SearchWeb": SearchWeb,
    "SelectFromSQLDatabase": SelectFromSQLDatabase,
    "SummarizeAllCodeInPath": SummarizeAllCodeInPath,
    "SummarizeCode": SummarizeCode,
    "WriteAndSaveProgram": WriteAndSaveProgram,
}
