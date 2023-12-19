from pathlib import Path

# Constants representing base and data directories
BASE_DIR = Path(__file__).resolve(strict=True).parent
DATA_DIR = BASE_DIR / "data"

# Constants for default configuration files
DEFAULT_CONFIG_FILE = DATA_DIR / "default_config.json"
CONFIG_FILE_BASE = DATA_DIR / "config.json"
