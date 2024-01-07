from fastapi import APIRouter, Body, Depends, HTTPException
from fastapi.params import Query

from nalgonda.dependencies.agent_manager import AgentManager, get_agent_manager
from nalgonda.dependencies.auth import get_current_active_user
from nalgonda.models.agent_config import AgentConfig
from nalgonda.models.auth import UserInDB
from nalgonda.persistence.agent_config_firestore_storage import AgentConfigFirestoreStorage

agent_router = APIRouter()


@agent_router.put("/agent/config", tags=["agents"])
async def update_agent_config(
    agent_config: AgentConfig = Body(...),
    agent_manager: AgentManager = Depends(get_agent_manager),
    current_user: UserInDB = Depends(get_current_active_user),
):
    agent_config.owner_id = current_user.username  # Ensure the agent is associated with the user
    agent_id = await agent_manager.create_or_update_agent(agent_config)
    return {"agent_id": agent_id}


@agent_router.get("/agent/config", tags=["agents"])
async def get_agent_config(
    agent_id: str = Query(..., description="Agent ID"),
    storage: AgentConfigFirestoreStorage = Depends(AgentConfigFirestoreStorage),
):
    config = storage.load(agent_id)
    if not config:
        raise HTTPException(status_code=404, detail="Agent configuration not found")
    return config
