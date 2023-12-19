# nalgonda/routers/v1/api/__init__.py

from fastapi import APIRouter

from .agency import agency_router

api_router = APIRouter(
    prefix="/api",
    responses={404: {"description": "Not found"}},
)

api_router.include_router(agency_router)
