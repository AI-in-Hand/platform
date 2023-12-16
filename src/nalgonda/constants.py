from pathlib import Path

# Base directory for the project
BASE_DIR = Path(__file__).parent.resolve()

# Directory constants
DATA_DIR = BASE_DIR / "data"

# File constants
DEFAULT_CONFIG_FILE = DATA_DIR / "default_config.json"
CONFIG_FILE_BASE = DATA_DIR / "config"
