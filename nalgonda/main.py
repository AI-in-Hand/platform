import json
import logging

import firebase_admin
import openai
from fastapi import FastAPI
from firebase_admin import credentials

from nalgonda.constants import DATA_DIR
from nalgonda.routers.v1 import v1_router
from nalgonda.settings import settings

openai.api_key = settings.openai_api_key

# Ensure data directory exists
DATA_DIR.mkdir(parents=True, exist_ok=True)

# Logging configuration
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)
# Silence passlib warning messages
logging.getLogger("passlib.handlers.bcrypt").setLevel(logging.ERROR)
logger = logging.getLogger(__name__)


# FastAPI app initialization
app = FastAPI()
app.include_router(v1_router)

# Initialize FireStore
if settings.google_credentials:
    cred_json = json.loads(settings.google_credentials)
    cred = credentials.Certificate(cred_json)
    firebase_admin.initialize_app(cred)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
