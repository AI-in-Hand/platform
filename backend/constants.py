from pathlib import Path

# Constants representing base and data directories
BASE_DIR = Path(__file__).resolve(strict=True).parent
DATA_DIR = BASE_DIR / "data"
AGENCY_DATA_DIR = DATA_DIR / "agency_data"

# Constants for default configuration files
DEFAULT_CACHE_EXPIRATION = 60 * 60 * 24  # 1 day

DEFAULT_OPENAI_API_TIMEOUT = 30.0  # seconds

INTERNAL_ERROR_MESSAGE = (
    "Something went wrong. We're investigating the issue. " "Please try again or report it using our chatbot widget."
)
