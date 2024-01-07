from fastapi import APIRouter, Body, HTTPException, Path

from nalgonda.models.agent_config import AgentConfig
from nalgonda.persistence.agent_config_firestore_storage import AgentConfigFirestoreStorage

agent_router = APIRouter()


@agent_router.put("/agent/config", tags=["agents"])
def update_agent_config(agent_config: AgentConfig = Body(...)):
    storage = AgentConfigFirestoreStorage()
    storage.save(agent_config)
    return {"message": "Agent configuration saved successfully"}


@agent_router.get("/agent/config", tags=["agents"])
def get_agent_config(agent_id: str = Path(..., description="The unique identifier of the agent configuration")):
    storage = AgentConfigFirestoreStorage()
    config = storage.load(agent_id)
    if not config:
        raise HTTPException(status_code=404, detail="Agent configuration not found")
    return config
