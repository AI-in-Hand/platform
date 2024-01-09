from fastapi import APIRouter, Body, Depends, HTTPException, Query

from nalgonda.dependencies.auth import get_current_active_user
from nalgonda.models.auth import UserInDB
from nalgonda.models.tool_config import ToolConfig
from nalgonda.persistence.tool_config_firestore_storage import ToolConfigFirestoreStorage

tool_router = APIRouter(tags=["tool"])


@tool_router.put("/tool/config")
def update_tool_config(
    tool_config: ToolConfig = Body(...),
    current_user: UserInDB = Depends(get_current_active_user),
):
    tool_config.owner_id = current_user.username  # Ensure the tool is associated with the user
    storage = ToolConfigFirestoreStorage()
    tool_id, tool_version = storage.save(tool_config)
    return {"tool_id": tool_id, "tool_version": tool_version}


@tool_router.get("/tool/config")
def get_tool_configs(user_id: str = Query(..., description="The unique identifier of the user")):
    storage = ToolConfigFirestoreStorage()
    tools = storage.load_by_user_id(user_id)
    if not tools:
        raise HTTPException(status_code=404, detail="No tool configurations found")
    return tools


@tool_router.put("/tool/approve")
def approve_tool_config(tool_id: str = Query(..., description="The unique identifier of the tool")):
    storage = ToolConfigFirestoreStorage()
    tool_config = storage.load_by_tool_id(tool_id)
    if not tool_config:
        raise HTTPException(status_code=404, detail="Tool configuration not found")

    storage.save(tool_config, approved=True)
    return {"message": "Tool configuration approved"}
