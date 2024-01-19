from fastapi import APIRouter, Body, Depends, HTTPException
from fastapi.params import Query

from nalgonda.dependencies.agent_manager import AgentManager, get_agent_manager
from nalgonda.dependencies.auth import get_current_active_user
from nalgonda.models.agent_config import AgentConfig
from nalgonda.models.auth import UserInDB
from nalgonda.persistence.agent_config_firestore_storage import AgentConfigFirestoreStorage

agent_router = APIRouter(tags=["agent"])


@agent_router.get("/agent")
async def get_agent_list(
    user_id: str = Query(..., description="The unique identifier of the user"),
    storage: AgentConfigFirestoreStorage = Depends(AgentConfigFirestoreStorage),
) -> list[AgentConfig]:
    agents = storage.load_by_user_id(user_id)
    if not agents:
        raise HTTPException(status_code=404, detail="No agency configuration found")
    return agents


@agent_router.get("/agent/config")
async def get_agent_config(
    agent_id: str = Query(..., description="The unique identifier of the agent"),
    storage: AgentConfigFirestoreStorage = Depends(AgentConfigFirestoreStorage),
) -> AgentConfig:
    config = storage.load_by_agent_id(agent_id)
    if not config:
        raise HTTPException(status_code=404, detail="Agent configuration not found")
    return config


@agent_router.put("/agent/config")
async def update_agent_config(
    agent_config: AgentConfig = Body(...),
    agent_manager: AgentManager = Depends(get_agent_manager),
    current_user: UserInDB = Depends(get_current_active_user),
) -> dict[str, str]:
    agent_config.owner_id = current_user.username  # Ensure the agent is associated with the user
    agent_id = await agent_manager.create_or_update_agent(agent_config)
    return {"agent_id": agent_id}
