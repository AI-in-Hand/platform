from fastapi import APIRouter

from .api import api_router
from .websocket import ws_router

v1_router = APIRouter(
    prefix="/v1",
    responses={404: {"description": "Not found"}},
)

v1_router.include_router(api_router)
v1_router.include_router(ws_router)
