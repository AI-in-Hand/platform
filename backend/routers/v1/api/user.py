from typing import Annotated

from fastapi import APIRouter, Body, Depends

from backend.dependencies.auth import get_current_user
from backend.dependencies.dependencies import get_user_secret_manager
from backend.models.auth import User
from backend.models.response_models import BaseResponse
from backend.services.user_secret_manager import UserSecretManager

user_router = APIRouter(tags=["user"])


@user_router.get("/user/settings/secrets")
async def get_secrets(
    current_user: Annotated[User, Depends(get_current_user)],
    user_secret_manager: UserSecretManager = Depends(get_user_secret_manager),
) -> list[str]:
    return user_secret_manager.get_secret_names(current_user.id)


@user_router.put("/user/settings/secrets")
async def update_secrets(
    current_user: Annotated[User, Depends(get_current_user)],
    user_secret: dict = Body(...),
    user_secret_manager: UserSecretManager = Depends(get_user_secret_manager),
) -> BaseResponse:
    user_secret_manager.update_secrets(user_id=current_user.id, secrets=user_secret)
    return BaseResponse(message="Environment configuration updated")
