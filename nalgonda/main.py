import json

import firebase_admin
import openai
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from firebase_admin import credentials
from pydantic import ValidationError
from starlette.staticfiles import StaticFiles

from nalgonda.utils.logging_utils import setup_logging

setup_logging()

from nalgonda.constants import BASE_DIR  # noqa  # isort:skip
from nalgonda.exception_handlers import bad_request_exception_handler, unhandled_exception_handler  # noqa  # isort:skip
from nalgonda.routers.v1 import v1_router  # noqa  # isort:skip
from nalgonda.settings import settings  # noqa  # isort:skip
from nalgonda.utils import init_webserver_folders  # noqa  # isort:skip

# just a placeholder for compatibility with agency-swarm
openai.api_key = "sk-1234567890"

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
v1_api_app.add_exception_handler(ValidationError, bad_request_exception_handler)
v1_api_app.add_exception_handler(Exception, unhandled_exception_handler)

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
