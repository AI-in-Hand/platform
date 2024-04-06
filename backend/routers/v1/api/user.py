from fastapi import APIRouter, Body, Depends
from pydantic import Annotated

from backend.dependencies.auth import get_current_user
from backend.dependencies.dependencies import get_env_config_manager
from backend.models.auth import User
from backend.models.response_models import BaseResponse
from backend.services.env_config_manager import EnvConfigManager

user_router = APIRouter(tags=["user"])


@user_router.get("/user/env-config")
async def get_env_config(
    current_user: Annotated[User, Depends(get_current_user)],
    env_config_manager: EnvConfigManager = Depends(get_env_config_manager),
) -> list[str]:
    return env_config_manager.get_config_keys(current_user.id)


@user_router.put("/user/env-config")
async def update_env_config(
    current_user: Annotated[User, Depends(get_current_user)],
    env_config: dict = Body(...),
    env_config_manager: EnvConfigManager = Depends(get_env_config_manager),
) -> BaseResponse:
    env_config_manager.update_config(user_id=current_user.id, env_config=env_config)
    return BaseResponse(message="Environment configuration updated")
