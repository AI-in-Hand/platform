from pathlib import Path

# File and Directory Constants
DATA_DIR = Path(__file__).resolve().parent / "data"
DEFAULT_CONFIG_FILE = DATA_DIR / "default_config.json"
CONFIG_FILE = DATA_DIR / "config"

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
