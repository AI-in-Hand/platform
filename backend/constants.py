from pathlib import Path

# Constants
DATA_DIR = Path(__file__).resolve().parent / "data"
ANALYST_DOC = DATA_DIR / "Requirement_Gathering_Guidelines_for_Analysts.txt"
ASSISTANT_JSON = DATA_DIR / "assistant.json"
REQUIREMENTS_DIR = DATA_DIR / "requirements"

ASSISTANT_NAME = "Software Analyst Assistant"
GPT_MODEL = "gpt-4-1106-preview"

ASSISTANT_TOOLS = [
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
]
