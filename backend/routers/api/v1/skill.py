import logging
from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Body, Depends, HTTPException, Query

from backend.dependencies.auth import get_current_superuser, get_current_user
from backend.dependencies.dependencies import get_skill_manager
from backend.models.auth import User
from backend.models.request_models import SkillExecutePostRequest
from backend.models.response_models import (
    BaseResponse,
    ExecuteSkillResponse,
    GetSkillResponse,
    SkillListResponse,
)
from backend.models.skill_config import SkillConfig
from backend.repositories.skill_config_storage import SkillConfigStorage
from backend.services.skill_executor import SkillExecutor
from backend.services.skill_manager import SkillManager

logger = logging.getLogger(__name__)

skill_router = APIRouter(tags=["skill"])


# TODO: add pagination support for skill list

# FIXME: current limitation on skills: we always use common skills (user_id=None).
# TODO: support dynamic loading of skills (save skills in /approve to Python files in backend/custom_tools,
#  and update the skill mapping).


@skill_router.get("/skill/list")
async def get_skill_list(
    current_user: Annotated[User, Depends(get_current_user)],
    manager: SkillManager = Depends(get_skill_manager),
) -> SkillListResponse:
    """Get a list of configs for the skills the current user has access to."""
    skills = manager.get_skill_list(current_user.id)
    return SkillListResponse(data=skills)


@skill_router.get("/skill")
async def get_skill_config(
    current_user: Annotated[User, Depends(get_current_user)],
    id: str = Query(..., description="The unique identifier of the skill"),
    manager: SkillManager = Depends(get_skill_manager),
) -> GetSkillResponse:
    """Get a skill configuration by ID.
    NOTE: currently this endpoint is not used in the frontend.
    """
    config = manager.get_skill_config(id)
    manager.check_user_permissions(config, current_user.id)
    return GetSkillResponse(data=config)


@skill_router.put("/skill")
async def create_skill_version(
    current_user: Annotated[User, Depends(get_current_user)],
    config: SkillConfig = Body(...),
    manager: SkillManager = Depends(get_skill_manager),
) -> SkillListResponse:
    """Create a new version of the skill configuration.
    NOTE: currently this endpoint is not fully supported.
    """
    skill_id, skill_version = manager.create_skill_version(config, current_user.id)
    configs = manager.get_skill_list(current_user.id)
    return SkillListResponse(data=configs, message=f"Version {skill_version} of the skill {skill_id} created")


@skill_router.delete("/skill")
async def delete_skill(
    current_user: Annotated[User, Depends(get_current_user)],
    id: str = Query(..., description="The unique identifier of the skill"),
    manager: SkillManager = Depends(get_skill_manager),
):
    """Delete a skill configuration."""
    manager.delete_skill(id, current_user.id)
    configs = manager.get_skill_list(current_user.id)
    return SkillListResponse(data=configs, message="Skill configuration deleted")


@skill_router.post("/skill/approve")
async def approve_skill(
    current_superuser: Annotated[User, Depends(get_current_superuser)],  # noqa: ARG001
    id: str = Query(..., description="The unique identifier of the skill"),
    storage: SkillConfigStorage = Depends(SkillConfigStorage),
):
    """Approve a skill configuration. This endpoint is only accessible to superusers (currently not accessible).
    NOTE: currently this endpoint is not used in the frontend, and you can only approve skills directly in the DB."""
    config = storage.load_by_id(id)
    if not config:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Skill not found")

    config.approved = True
    storage.save(config)
    return BaseResponse(message="Skill configuration approved")


@skill_router.post("/skill/execute")
async def execute_skill(
    current_user: Annotated[User, Depends(get_current_user)],
    payload: SkillExecutePostRequest = Body(...),
    manager: SkillManager = Depends(get_skill_manager),
    executor: SkillExecutor = Depends(SkillExecutor),
) -> ExecuteSkillResponse:
    """Execute a skill."""
    config = manager.get_skill_config(payload.id)
    manager.check_user_permissions(config, current_user.id)

    # check if the current_user has permissions to execute the skill
    if config.user_id:
        manager.check_user_permissions(config, current_user.id)

    # check if the skill is approved
    if not config.approved:
        raise HTTPException(status_code=HTTPStatus.FORBIDDEN, detail="Skill not approved")

    output = executor.execute_skill(config.title, payload.user_prompt)

    return ExecuteSkillResponse(data=output)
