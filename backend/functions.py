import json
import os
from pathlib import Path

from openai import OpenAI
from openai.types.beta.threads import RequiredActionFunctionToolCall

from prompts import assistant_instructions

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

DATA_DIR = Path(os.path.dirname(os.path.abspath(__file__))) / "data"
ASSISTANT_JSON = DATA_DIR / "assistant.json"
ANALYST_DOC = DATA_DIR / "Requirement_Gathering_Guidelines_for_Analysts.txt"


def load_or_create_assistant(client):
    if os.path.exists(ASSISTANT_JSON):
        with open(ASSISTANT_JSON, "r") as file:
            assistant_data = json.load(file)
            return assistant_data["assistant_id"]
    else:
        with open(ANALYST_DOC, "rb") as file_to_read:
            file = client.files.create(file=file_to_read, purpose="assistants")
        assistant = client.beta.assistants.create(
            instructions=assistant_instructions,
            model="gpt-4-1106-preview",
            tools=[
                {"type": "retrieval"},
                {
                    "type": "function",
                    "function": {
                        "name": "save_requirements",
                        "description": "Save requirements document.",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "user_responses": {
                                    "type": "array",
                                    "items": {
                                        "type": "object",
                                        "properties": {
                                            "question": {"type": "string"},
                                            "answer": {"type": "string"},
                                        },
                                        "required": ["question", "answer"],
                                    },
                                },
                                "requirements_text": {"type": "string"},
                            },
                        },
                        "required": ["user_responses", "requirements_text"],
                    },
                },
            ],
            file_ids=[file.id],
        )
        with open(ASSISTANT_JSON, "w") as file:
            json.dump({"assistant_id": assistant.id}, file)
        return assistant.id


def save_requirements(user_responses: dict, requirements_text: str, thread_id, run_id):
    file_path = DATA_DIR / f"requirements_{thread_id}_{run_id}.txt"
    with open(file_path, "w") as file:
        for response in user_responses:
            file.write(f"{response['question']}: {response['answer']}\n")
        file.write("\n\n Requirements:\n\n")
        file.write(requirements_text)
    return {
        "status": "Success",
        "message": "Requirements document saved.",
        "path": file_path.as_posix(),
    }


available_functions = {
    "save_requirements": save_requirements,
}


def handle_action(tool_call: RequiredActionFunctionToolCall, thread_id, run_id):
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
