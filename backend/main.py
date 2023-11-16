import os
from time import sleep

import openai
from flask import Flask, request, jsonify
from packaging import version

import functions


def check_openai_version():
    """ Ensure the OpenAI version is compatible. """
    required_version = version.parse("1.1.1")
    current_version = version.parse(openai.__version__)
    if current_version < required_version:
        raise ValueError(f"Error: OpenAI version {openai.__version__} is less than the required version 1.1.1")


def get_openai_api_key():
    """ Fetch OpenAI API key from environment variables. """
    return os.environ['OPENAI_API_KEY']


def create_app():
    """ Create and configure the Flask app. """
    app = Flask(__name__)
    check_openai_version()

    openai_api_key = get_openai_api_key()
    client = openai.OpenAI(api_key=openai_api_key)

    assistant_id = functions.create_assistant(client)

    # Start conversation thread
    @app.route('/start', methods=['GET'])
    def start_conversation():
        print("Starting a new conversation...")
        thread = client.beta.threads.create()
        print(f"New thread created with ID: {thread.id}")
        return jsonify({"thread_id": thread.id})

    # Generate response
    @app.route('/chat', methods=['POST'])
    def chat():
        data = request.json
        thread_id = data.get('thread_id')
        user_input = data.get('message', '')

        if not thread_id:
            print("Error: Missing thread_id")
            return jsonify({"error": "Missing thread_id"}), 400

        print(f"Received message: {user_input} for thread ID: {thread_id}")

        # Add the user's message to the thread
        client.beta.threads.messages.create(thread_id=thread_id, role="user", content=user_input)

        # Run the Assistant
        run = client.beta.threads.runs.create(thread_id=thread_id, assistant_id=assistant_id)

        # Check if the Run requires action (function call)
        while True:
            run_status = client.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run.id)
            print(f"Run status: {run_status.status}")
            if run_status.status == "completed":
                break
            sleep(1)  # Wait for a second before checking again

        # Retrieve and return the latest message from the assistant
        messages = client.beta.threads.messages.list(thread_id=thread_id)
        response = messages.data[0].content[0].text.value
        print(f"Assistant response: {response}")
        return jsonify({"response": response})

    return app


def main():
    """ Main entry point for the application. """
    app = create_app()
    app.run(host='0.0.0.0', port=8080)


if __name__ == '__main__':
    main()
