from fastapi import APIRouter

from backend.routers.api.v1 import v1_router

api_router = APIRouter(
    prefix="/api",
    responses={404: {"description": "Not found"}},
)

api_router.include_router(v1_router)
# api_router.include_router(ws_router)  # Uncomment this line to enable WebSocket support
