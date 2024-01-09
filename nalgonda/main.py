import json
import logging

import firebase_admin
import openai
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from firebase_admin import credentials
from starlette.staticfiles import StaticFiles

from nalgonda.constants import BASE_DIR
from nalgonda.routers.v1 import v1_router
from nalgonda.settings import settings
from nalgonda.utils import init_webserver_folders

openai.api_key = settings.openai_api_key

# Logging configuration
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger(__name__)

# FastAPI app initialization
app = FastAPI()

# allow cross-origin requests for testing on localhost:800* ports only
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8000",
        "http://127.0.0.1:8000",
        "http://localhost:8001",
        "http://localhost:8081",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# init folders skills, workdir, static, files etc
folders = init_webserver_folders(root_file_path=BASE_DIR)

v1_api_app = FastAPI(root_path="/v1")
v1_api_app.include_router(v1_router)

# mount an api route such that the main route serves the ui and the /api
app.mount("/v1", v1_api_app)
app.mount("/", StaticFiles(directory=folders["static_folder_root"], html=True), name="ui")

# Initialize FireStore
if settings.google_credentials:
    cred_json = json.loads(settings.google_credentials)
    cred = credentials.Certificate(cred_json)
    firebase_admin.initialize_app(cred)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
