import logging
from datetime import UTC, datetime
from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Body, Depends, HTTPException, Query

from backend.dependencies.auth import get_current_superuser, get_current_user
from backend.models.auth import User
from backend.models.request_models import SkillExecutePostRequest
from backend.models.response_models import (
    BaseResponse,
    CreateSkillVersionData,
    CreateSkillVersionResponse,
    ExecuteSkillResponse,
    GetSkillListResponse,
    GetSkillResponse,
)
from backend.models.skill_config import SkillConfig
from backend.repositories.skill_config_firestore_storage import SkillConfigFirestoreStorage
from backend.services.skill_service import SkillService, generate_skill_description

logger = logging.getLogger(__name__)
skill_router = APIRouter(tags=["skill"])


# FIXME: current limitation on skills: we always use common skills (owner_id=None).
# TODO: support dynamic loading of skills.


@skill_router.get("/skill/list")
async def get_skill_list(
    current_user: Annotated[User, Depends(get_current_user)],
    storage: SkillConfigFirestoreStorage = Depends(SkillConfigFirestoreStorage),
) -> GetSkillListResponse:
    """Get a list of configs for all skills."""
    skills = storage.load_by_owner_id(current_user.id) + storage.load_by_owner_id(None)
    return GetSkillListResponse(data=skills)


@skill_router.get("/skill")
async def get_skill_config(
    current_user: Annotated[User, Depends(get_current_user)],
    id: str = Query(..., description="The unique identifier of the skill"),
    storage: SkillConfigFirestoreStorage = Depends(SkillConfigFirestoreStorage),
) -> GetSkillResponse:
    """Get a skill configuration by ID.
    NOTE: currently this endpoint is not used in the frontend.
    """
    config = storage.load_by_id(id)
    if not config:
        logger.warning(f"Skill not found: {id}, user: {current_user.id}")
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Skill not found")
    # check if the current_user has permissions to get the skill config
    if config.owner_id and config.owner_id != current_user.id:
        logger.warning(f"User {current_user.id} does not have permissions to get the skill: {config.id}")
        raise HTTPException(status_code=HTTPStatus.FORBIDDEN, detail="Forbidden")
    return GetSkillResponse(data=config)


@skill_router.post("/skill")
async def create_skill_version(
    current_user: Annotated[User, Depends(get_current_user)],
    config: SkillConfig = Body(...),
    storage: SkillConfigFirestoreStorage = Depends(SkillConfigFirestoreStorage),
) -> CreateSkillVersionResponse:
    """Create a new version of the skill configuration."""
    skill_config_db = None

    # support template configs:
    if not config.owner_id:
        config.id = None
    else:
        # check if the current_user has permissions
        if config.id:
            skill_config_db = storage.load_by_id(config.id)
            if not skill_config_db:
                logger.warning(f"Skill not found: {config.id}, user: {current_user.id}")
                raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Skill not found")
            if skill_config_db.owner_id != current_user.id:
                logger.warning(f"User {current_user.id} does not have permissions to update the skill: {config.id}")
                raise HTTPException(status_code=HTTPStatus.FORBIDDEN, detail="Forbidden")

    # Ensure the skill is associated with the current user
    config.owner_id = current_user.id

    config.version = skill_config_db.version + 1 if skill_config_db else 1
    config.approved = False
    config.timestamp = datetime.now(UTC).isoformat()

    if not config.description and config.content:
        config.description = generate_skill_description(config.content)

    skill_id, skill_version = storage.save(config)
    return CreateSkillVersionResponse(data=CreateSkillVersionData(id=skill_id, version=skill_version))


@skill_router.post("/skill/approve")
async def approve_skill(
    current_superuser: Annotated[User, Depends(get_current_superuser)],  # noqa: ARG001
    id: str = Query(..., description="The unique identifier of the skill"),
    storage: SkillConfigFirestoreStorage = Depends(SkillConfigFirestoreStorage),
):
    """Approve a skill configuration."""
    config = storage.load_by_id(id)
    if not config:
        logger.warning(f"Skill not found: {id}, user: {current_superuser.id}")
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Skill not found")

    config.approved = True

    storage.save(config)
    return BaseResponse(message="Skill configuration approved")


@skill_router.post("/skill/execute")
async def execute_skill(
    current_user: Annotated[User, Depends(get_current_user)],
    request: SkillExecutePostRequest,
    storage: SkillConfigFirestoreStorage = Depends(SkillConfigFirestoreStorage),
    skill_service: SkillService = Depends(SkillService),
) -> ExecuteSkillResponse:
    """Execute a skill."""
    config = storage.load_by_id(request.id)
    if not config:
        logger.warning(f"Skill not found: {request.id}, user: {current_user.id}")
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Skill not found")

    # check if the current_user has permissions to execute the skill
    if config.owner_id and config.owner_id != current_user.id:
        logger.warning(f"User {current_user.id} does not have permissions to execute the skill: {config.id}")
        raise HTTPException(status_code=HTTPStatus.FORBIDDEN, detail="Forbidden")

    # check if the skill is approved
    if not config.approved:
        logger.warning(f"Skill not approved: {config.id}, user: {current_user.id}")
        raise HTTPException(status_code=HTTPStatus.FORBIDDEN, detail="Skill not approved")

    output = skill_service.execute_skill(config.title, request.user_prompt)

    return ExecuteSkillResponse(data=output)
