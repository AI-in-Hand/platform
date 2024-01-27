from pathlib import Path

# Constants representing base and data directories
BASE_DIR = Path(__file__).resolve(strict=True).parent
DATA_DIR = BASE_DIR / "data"
AGENCY_DATA_DIR = DATA_DIR / "agency_data"

# Constants for default configuration files
DEFAULT_CACHE_EXPIRATION = 60 * 60 * 24  # 1 day
