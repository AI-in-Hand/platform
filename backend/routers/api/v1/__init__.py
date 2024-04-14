from fastapi import APIRouter

from backend.routers.api.v1.agency import agency_router
from backend.routers.api.v1.agent import agent_router
from backend.routers.api.v1.message import message_router
from backend.routers.api.v1.session import session_router
from backend.routers.api.v1.skill import skill_router
from backend.routers.api.v1.user import user_router
from backend.routers.api.v1.version import version_router

v1_router = APIRouter(
    prefix="/v1",
    responses={404: {"description": "Not found"}},
)

v1_router.include_router(skill_router)
v1_router.include_router(agent_router)
v1_router.include_router(agency_router)
v1_router.include_router(session_router)
v1_router.include_router(message_router)
v1_router.include_router(version_router)
v1_router.include_router(user_router)
