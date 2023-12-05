import os
from pathlib import Path

# File and Directory Constants
DATA_DIR = Path(__file__).resolve().parent / "data"

# Assistant Configuration
GPT_MODEL = os.getenv("GPT_MODEL", "gpt-4-1106-preview")

# Assistant Tools Configuration
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
