from fastapi import APIRouter, Body, Depends, HTTPException, Path, Query

from nalgonda.dependencies.auth import get_current_active_user
from nalgonda.models.auth import UserInDB
from nalgonda.models.tool_config import ToolConfig
from nalgonda.persistence.tool_config_firestore_storage import ToolConfigFirestoreStorage

router = APIRouter()


@router.put("/tools/{tool_name}/config", tags=["tools"])
def update_tool_config(
    tool_config: ToolConfig = Body(...),
    current_user: UserInDB = Depends(get_current_active_user),
):
    tool_config.owner_id = current_user.username  # Ensure the tool is associated with the user
    storage = ToolConfigFirestoreStorage()
    storage.save(tool_config)
    return {"message": "Tool configuration saved successfully", "version": tool_config.version}


@router.get("/tools/config", tags=["tools"])
def get_tools_configs(user_id: str = Query(..., description="The unique identifier of the user")):
    storage = ToolConfigFirestoreStorage()
    tools = storage.load_by_user_id(user_id)
    if not tools:
        raise HTTPException(status_code=404, detail="No tool configurations found")
    return tools


@router.put("/tools/{tool_id}/approve", tags=["tools"])
def approve_tool_config(tool_id: str = Path(..., description="The unique identifier of the tool configuration")):
    storage = ToolConfigFirestoreStorage()
    tool_config = storage.load_by_tool_id(tool_id)
    if not tool_config:
        raise HTTPException(status_code=404, detail="Tool configuration not found")
    tool_config.approved = True
    storage.save(tool_config)
    return {"message": "Tool configuration approved successfully"}
