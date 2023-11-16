import json
import os

ANALYST_DOC = "Software_Development_Guidelines_for_Analysts.txt"


def get_root_dir():
    """ Get the root directory where data files are located. """
    current_dir = os.path.dirname(os.path.realpath(__file__))
    return os.path.join(current_dir, 'data/')


def get_assistant_file_path(root_dir):
    """ Get the file path for assistant.json. """
    return os.path.join(root_dir, 'assistant.json')


def load_existing_assistant(file_path):
    """ Load existing assistant data from file. """
    try:
        with open(file_path, 'r') as file:
            return json.load(file)['assistant_id']
    except (IOError, KeyError):
        return None


def create_new_assistant(client, root_dir):
    """ Create a new assistant and save its ID. """
    knowledge_doc = os.path.join(root_dir, ANALYST_DOC)

    try:
        with open(knowledge_doc, "rb") as doc_file:
            file = client.files.create(file=doc_file, purpose='assistants')

        assistant = client.beta.assistants.create(
            instructions="""\
The assistant, Software Development Analyst, has been programmed to gather user requirements. 
A Document has been provided with information on the methodology \
of this process. 
Strictly follow the instructions to achieve a goal: to generate and output "requirements.txt" document 
(in case the user project satisfies the limitations described in the attached Document). """,
            model="gpt-4-1106-preview",
            tools=[{"type": "retrieval"}],
            file_ids=[file.id]
        )

        assistant_file_path = get_assistant_file_path(root_dir)
        with open(assistant_file_path, 'w') as file:
            json.dump({'assistant_id': assistant.id}, file)

        return assistant.id
    except IOError as e:
        print(f"Error creating new assistant: {e}")
        return None


def create_assistant(client):
    """ Create an assistant or load an existing one. """
    root_dir = get_root_dir()
    assistant_file_path = get_assistant_file_path(root_dir)

    assistant_id = None
    if os.path.exists(assistant_file_path) and os.path.getsize(assistant_file_path) > 0:
        assistant_id = load_existing_assistant(assistant_file_path)

    if assistant_id is None:
        print("Creating a new assistant...")
        assistant_id = create_new_assistant(client, root_dir)

    return assistant_id
