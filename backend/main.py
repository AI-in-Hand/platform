from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from openai import AuthenticationError as OpenAIAuthenticationError
from pydantic import ValidationError
from starlette.staticfiles import StaticFiles

from backend.exceptions import UnsetVariableError
from backend.routers.api import api_router
from backend.routers.websocket import websocket_router
from backend.utils.logging_utils import setup_logging

setup_logging()

from backend.constants import BASE_DIR  # noqa  # isort:skip
from backend.exception_handlers import (  # noqa  # isort:skip
    pydantic_validation_error_handler,
    http_exception_handler,
    unhandled_exception_handler,
    request_validation_error_handler,
    openai_authentication_error_handler,
    unset_variable_error_handler,
)

from backend.routers.api.v1 import v1_router  # noqa  # isort:skip
from backend.settings import settings  # noqa  # isort:skip
from backend.utils import init_webserver_folders, init_firebase_app, patch_openai_client  # noqa  # isort:skip


init_firebase_app()

patch_openai_client()

# FastAPI app initialization
app = FastAPI()

# allow cross-origin requests for testing on localhost:800* ports only
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:8000",
        "http://localhost:8000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# init folders skills, workdir, static, files etc
folders = init_webserver_folders(root_file_path=BASE_DIR)

api_app = FastAPI(root_path="/api")
api_app.include_router(api_router)
api_app.add_exception_handler(ValidationError, pydantic_validation_error_handler)
api_app.add_exception_handler(RequestValidationError, request_validation_error_handler)
api_app.add_exception_handler(HTTPException, http_exception_handler)
api_app.add_exception_handler(OpenAIAuthenticationError, openai_authentication_error_handler)
api_app.add_exception_handler(UnsetVariableError, unset_variable_error_handler)
api_app.add_exception_handler(Exception, unhandled_exception_handler)

ws_app = FastAPI(root_path="/ws")
ws_app.include_router(websocket_router)

# mount an api route such that the main route serves the ui and the /api
app.mount("/api", api_app)
app.mount("/ws", ws_app)
app.mount("/", StaticFiles(directory=folders["static_folder_root"], html=True), name="ui")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
