from pathlib import Path

# Constants representing base and data directories
BASE_DIR = Path(__file__).resolve(strict=True).parent
DATA_DIR = BASE_DIR / "data"
AGENCY_DATA_DIR = DATA_DIR / "agency_data"
DEFAULT_CONFIGS_DIR = DATA_DIR / "default_configs"
AGENCY_CONFIGS_DIR = DEFAULT_CONFIGS_DIR / "agency"
AGENT_CONFIGS_DIR = DEFAULT_CONFIGS_DIR / "agent"

# Constants for default configuration files
DEFAULT_AGENCY_CONFIG_FILE = AGENCY_CONFIGS_DIR / "default_config.json"
DEFAULT_AGENT_CONFIG_FILE = AGENT_CONFIGS_DIR / "default_config.json"
