from fastapi import APIRouter

from backend.version import VERSION

version_router = APIRouter(
    tags=["version"],
)


@version_router.get("/version")
async def get_version():
    return {
        "status": True,
        "message": "Version retrieved successfully",
        "data": {"version": VERSION},
    }
