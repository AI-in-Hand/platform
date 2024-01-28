from typing import Annotated

from fastapi import APIRouter, Body, Depends, HTTPException, Query
from starlette.status import HTTP_403_FORBIDDEN, HTTP_404_NOT_FOUND

from nalgonda.dependencies.auth import get_current_active_user, get_current_superuser
from nalgonda.models.auth import UserInDB
from nalgonda.models.tool_config import ToolConfig
from nalgonda.persistence.tool_config_firestore_storage import ToolConfigFirestoreStorage
from nalgonda.services.tool_service import generate_tool_description

tool_router = APIRouter(tags=["tool"])


# FIXME: current limitation on tools: we always use common tools (owner_id=None).
# What needs to be done: support dynamic loading of tools.


@tool_router.get("/tool/list")
async def get_tool_list(
    current_user: Annotated[UserInDB, Depends(get_current_active_user)],
    storage: ToolConfigFirestoreStorage = Depends(ToolConfigFirestoreStorage),
) -> list[ToolConfig]:
    tools = storage.load_by_owner_id(current_user.id) + storage.load_by_owner_id(None)
    return tools


@tool_router.get("/tool")
async def get_tool_config(
    current_user: Annotated[UserInDB, Depends(get_current_active_user)],
    tool_id: str = Query(..., description="The unique identifier of the tool"),
    storage: ToolConfigFirestoreStorage = Depends(ToolConfigFirestoreStorage),
) -> ToolConfig:
    tool_config = storage.load_by_tool_id(tool_id)
    if not tool_config:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="Tool not found")
    # check if the current_user has permissions to get the tool config
    if tool_config.owner_id and tool_config.owner_id != current_user.id:
        raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail="Forbidden")
    return tool_config


@tool_router.post("/tool")
async def create_tool_version(
    current_user: Annotated[UserInDB, Depends(get_current_active_user)],
    tool_config: ToolConfig = Body(...),
    storage: ToolConfigFirestoreStorage = Depends(ToolConfigFirestoreStorage),
):
    tool_config_db = None

    # support template configs:
    if not tool_config.owner_id:
        tool_config.tool_id = None
    else:
        # check if the current_user has permissions
        if tool_config.tool_id:
            tool_config_db = storage.load_by_tool_id(tool_config.tool_id)
            if not tool_config_db:
                raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="Tool not found")
            if tool_config_db.owner_id != current_user.id:
                raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail="Forbidden")

    # Ensure the tool is associated with the current user
    tool_config.owner_id = current_user.id

    # Increment version and set approved to False
    tool_config.version = tool_config_db.version + 1 if tool_config_db else 1
    tool_config.approved = False

    if not tool_config.description and tool_config.code:
        tool_config.description = generate_tool_description(tool_config.code)

    tool_id, tool_version = storage.save(tool_config)
    return {"tool_id": tool_id, "tool_version": tool_version}


@tool_router.post("/tool/approve")
async def approve_tool(
    current_superuser: Annotated[UserInDB, Depends(get_current_superuser)],  # noqa: ARG001
    tool_id: str = Query(..., description="The unique identifier of the tool"),
    storage: ToolConfigFirestoreStorage = Depends(ToolConfigFirestoreStorage),
):
    tool_config = storage.load_by_tool_id(tool_id)
    if not tool_config:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="Tool not found")

    tool_config.approved = True

    storage.save(tool_config)
    return {"message": "Tool configuration approved"}
