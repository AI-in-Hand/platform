import os
import json

ROOT_DIR = ...

ANALYST_DOC = "Software_Development_Guidelines_for_Analysts.docx"
DEVELOPER_DOC = "Software_Development_Guidelines_for_Developers.docx"


def create_assistant(client):
    assistant_file_path = 'assistant.json'

    # Check if the assistant file exists and has content
    if os.path.exists(assistant_file_path) and os.path.getsize(assistant_file_path) > 0:
        with open(assistant_file_path, 'r') as file:
            assistant_data = json.load(file)
            assistant_id = assistant_data['assistant_id']
            print("Loaded existing assistant ID")
    else:
        file = client.files.create(file=open(ANALYST_DOC, "rb"),
                                   purpose='assistants')

        assistant = client.beta.assistants.create(instructions="""
The assistant, Software Development Analyst, has been programmed to gather user requirements. 
A Document has been provided with information on the methodology of this process. 
Strictly follow the instructions to achieve a goal: to generate and output a Requirements Document 
(in case the user project satisfies the limitations described in the Document).
""",
                                                  model="gpt-4-1106-preview",
                                                  tools=[{
                                                      "type": "retrieval"
                                                  }],
                                                  file_ids=[file.id])
        with open(assistant_file_path, 'w') as file:
            json.dump({'assistant_id': assistant.id}, file)
        print("Created a new assistant and saved the ID.")

        assistant_id = assistant.id

    return assistant_id
