import json
import os
import time

import openai
from flask import Flask, jsonify, request
from openai.types.beta.threads.run_submit_tool_outputs_params import ToolOutput

import functions
from constants import ANALYST_DOC, ASSISTANT_JSON, DATA_DIR, REQUIREMENTS_DIR

# Ensure directories exist
DATA_DIR.mkdir(exist_ok=True)
REQUIREMENTS_DIR.mkdir(exist_ok=True)


def create_app():
    app = Flask(__name__)
    client = setup_openai_client()
    assistant_id = functions.get_assistant(client, assistant_file_path=ASSISTANT_JSON, analyst_doc_path=ANALYST_DOC)

    @app.route("/start", methods=["GET"])
    def start_conversation():
        thread = client.beta.threads.create()
        return jsonify({"thread_id": thread.id})

    @app.route("/chat", methods=["POST"])
    def chat():
        data = request.json
        thread_id = data["thread_id"]  # validate request after switching to FastAPI
        user_input = data.get("message", "")

        # A workaround for failures during "requires_action" status function calling (to allow for bug fixing)
        last_run = client.beta.threads.runs.list(thread_id=thread_id, limit=1, order="desc")
        if last_run.data and (last_run.data[-1].status == "requires_action"):
            run = last_run.data[-1]
        else:
            client.beta.threads.messages.create(thread_id=thread_id, role="user", content=user_input)
            run = client.beta.threads.runs.create(thread_id=thread_id, assistant_id=assistant_id)

        while True:
            run = client.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run.id)

            while run.status in ["queued", "in_progress"]:
                run = client.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run.id)
                time.sleep(1)

            if run.status == "requires_action":
                tool_calls = run.required_action.submit_tool_outputs.tool_calls
                tool_outputs = []
                for tool_call in tool_calls:
                    print(tool_call.function)
                    output = functions.handle_action(tool_call, thread_id, run.id)
                    tool_outputs.append(ToolOutput(tool_call_id=tool_call.id, output=json.dumps(output)))

                client.beta.threads.runs.submit_tool_outputs(
                    thread_id=thread_id,
                    run_id=run.id,
                    tool_outputs=tool_outputs,
                )

            elif run.status == "failed":
                return jsonify({"error": f"Run failed. Error: {run.last_error}"})
            else:
                messages = client.beta.threads.messages.list(thread_id=thread_id)

                response = messages.data[0].content[0].text.value
                return jsonify({"response": response})

    return app


def setup_openai_client():
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        raise ValueError("OpenAI API key is not set")
    return openai.OpenAI(api_key=openai_api_key)


def main():
    app = create_app()
    app.run(host="0.0.0.0", port=8080)


if __name__ == "__main__":
    main()
