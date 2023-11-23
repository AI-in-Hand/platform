import json
import os

from openai import OpenAI

from prompts import assistant_instructions

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


TXT_FILE_NAME = "Requirement_Gathering_Guidelines_for_Analysts.txt"


def create_assistant(client):
    assistant_file_path = "assistant.json"

    if os.path.exists(assistant_file_path):
        with open(assistant_file_path, "r") as file:
            assistant_data = json.load(file)
            return assistant_data["assistant_id"]
    else:
        with open(TXT_FILE_NAME, "rb") as file_to_read:
            file = client.files.create(file=file_to_read, purpose="assistants")
        assistant = client.beta.assistants.create(
            instructions=assistant_instructions,
            model="gpt-4-1106-preview",
            tools=[
                {"type": "retrieval"},
                {"type": "function"},
            ],
            file_ids=[file.id],
        )
        with open(assistant_file_path, "w") as file:
            json.dump({"assistant_id": assistant.id}, file)
        return assistant.id


def handle_action(tool_call, thread_id, run_id):
    if tool_call.function.name == "save_requirements":
        arguments = json.loads(tool_call.function.arguments)
        return save_requirements(arguments["user_responses"], thread_id, run_id)
    # Additional function calls can be handled here


def save_requirements(user_responses, thread_id, run_id):
    file_path = f"requirements/{thread_id}_{run_id}.txt"
    with open(file_path, "w") as file:
        for response in user_responses:
            file.write(f"{response['question']}: {response['answer']}\n")
    return {
        "status": "Success",
        "message": "Requirements document saved.",
        "path": file_path,
    }
