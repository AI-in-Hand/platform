# nalgonda/routers/v1/api/__init__.py

from fastapi import APIRouter

from .agency import agency_router
from .agent import agent_router
from .auth import auth_router
from .message import message_router
from .thread import thread_router
from .tool import tool_router

api_router = APIRouter(
    prefix="/api",
    responses={404: {"description": "Not found"}},
)

api_router.include_router(agency_router)
api_router.include_router(thread_router)
api_router.include_router(message_router)
api_router.include_router(agent_router)
api_router.include_router(tool_router)
api_router.include_router(auth_router)
