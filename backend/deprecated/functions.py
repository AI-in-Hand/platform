import json
from pathlib import Path

from openai.types.beta.threads import RequiredActionFunctionToolCall

from constants import ASSISTANT_NAME, ASSISTANT_TOOLS, GPT_MODEL, REQUIREMENTS_DIR
from prompts import assistant_instructions


def get_assistant(client, assistant_file_path: Path, analyst_doc_path: Path) -> str:
    if assistant_file_path.exists():
        assistant_id = load_assistant(assistant_file_path)
        update_assistant(client, assistant_id, analyst_doc_path)
        return assistant_id
    else:
        return create_new_assistant(client, assistant_file_path, analyst_doc_path)


def load_assistant(file_path: Path) -> str:
    with open(file_path, "r") as file:
        assistant_data = json.load(file)
    return assistant_data["assistant_id"]


def create_new_assistant(client, assistant_file_path: Path, analyst_doc_path: Path) -> str:
    with open(analyst_doc_path, "rb") as file_to_read:
        file = client.files.create(file=file_to_read, purpose="assistants")
    assistant = client.beta.assistants.create(
        name=ASSISTANT_NAME,
        instructions=assistant_instructions,
        model=GPT_MODEL,
        tools=ASSISTANT_TOOLS,
        file_ids=[file.id],
    )

    with open(assistant_file_path, "w") as file:
        json.dump({"assistant_id": assistant.id}, file)
    return assistant.id


def update_assistant(client, assistant_id: str, analyst_doc_path: Path):
    with open(analyst_doc_path, "rb") as file_to_read:
        file = client.files.create(file=file_to_read, purpose="assistants")
    client.beta.assistants.update(
        name=ASSISTANT_NAME,
        assistant_id=assistant_id,
        instructions=assistant_instructions,
        model=GPT_MODEL,
        tools=ASSISTANT_TOOLS,
        file_ids=[file.id],
    )


def save_requirements(user_responses: dict, requirements_text: str, thread_id: str, run_id: str) -> dict:
    file_path = REQUIREMENTS_DIR / f"requirements_{thread_id}_{run_id}.txt"
    with open(file_path, "w") as file:
        for response in user_responses:
            file.write(f"{response['question']}: {response['answer']}")
        file.write("\n\n")
        file.write(requirements_text)
    return {
        "status": "Success",
        "message": "Requirements document saved.",
        "path": file_path.as_posix(),
    }


available_functions = {
    "save_requirements": save_requirements,
}


def handle_action(tool_call: RequiredActionFunctionToolCall, thread_id: str, run_id: str) -> dict:
    function_name = tool_call.function.name
    function_to_call = available_functions[function_name]
    try:
        function_args = json.loads(tool_call.function.arguments)
    except json.decoder.JSONDecodeError as e:
        return {"status": "Error", "message": f"Invalid arguments: {e}"}

    try:
        function_response = function_to_call(**function_args, thread_id=thread_id, run_id=run_id)
    except Exception as e:
        return {"status": "Error", "message": f"Error while executing function: {e}"}

    return function_response
