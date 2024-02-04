# nalgonda/routers/v1/api/__init__.py

from fastapi import APIRouter

from .agency import agency_router
from .agent import agent_router
from .auth import auth_router
from .message import message_router
from .session import session_router
from .tool import tool_router
from .version import version_router

api_router = APIRouter(
    prefix="/api",
    responses={404: {"description": "Not found"}},
)

api_router.include_router(auth_router)
api_router.include_router(tool_router)
api_router.include_router(agent_router)
api_router.include_router(agency_router)
api_router.include_router(session_router)
api_router.include_router(message_router)
api_router.include_router(version_router)
