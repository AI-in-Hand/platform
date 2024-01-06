from fastapi import APIRouter, Body, HTTPException, Path

from nalgonda.models.agent_config import AgentConfig
from nalgonda.persistence.agent_config_firestore_storage import AgentConfigFirestoreStorage

router = APIRouter()


@router.put("/agent/{agent_id}/config", tags=["agents"])
def update_agent_config(
    agent_id: str = Path(..., description="The unique identifier of the agent configuration"),
    agent_config: AgentConfig = Body(...),
):
    storage = AgentConfigFirestoreStorage(agent_id)
    storage.save(agent_config)
    return {"message": "Agent configuration saved successfully"}


@router.get("/agent/{agent_id}/config", tags=["agents"])
def get_agent_config(agent_id: str = Path(..., description="The unique identifier of the agent configuration")):
    storage = AgentConfigFirestoreStorage(agent_id)
    config = storage.load()
    if not config:
        raise HTTPException(status_code=404, detail="Agent configuration not found")
    return config
