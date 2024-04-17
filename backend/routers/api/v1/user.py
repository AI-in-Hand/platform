from typing import Annotated

from fastapi import APIRouter, Body, Depends

from backend.dependencies.auth import get_current_user
from backend.dependencies.dependencies import get_user_secret_manager
from backend.models.auth import User
from backend.models.response_models import UserSecretsResponse
from backend.services.user_secret_manager import UserSecretManager

user_router = APIRouter(tags=["user"])


@user_router.get("/user/settings/secrets")
async def get_secrets(
    current_user: Annotated[User, Depends(get_current_user)],
    user_secret_manager: UserSecretManager = Depends(get_user_secret_manager),
) -> UserSecretsResponse:
    """
    Retrieve a list of secret names associated with the current user.
    This endpoint fetches the names of all secrets stored for the authenticated user. It does not return the secret
    values, ensuring sensitive information remains secure.
    """
    user_secrets = user_secret_manager.get_secret_names(current_user.id)
    return UserSecretsResponse(data=user_secrets)


@user_router.put("/user/settings/secrets")
async def update_secrets(
    current_user: Annotated[User, Depends(get_current_user)],
    user_secrets: dict[str, str] = Body(...),
    user_secret_manager: UserSecretManager = Depends(get_user_secret_manager),
) -> UserSecretsResponse:
    """
    Update or create the secrets associated with the current user.

    This endpoint allows for updating the user's secrets.
    Existing secrets are updated based on the keys provided in the request body.
    This functionality supports partial updates; secrets with "" values remain unchanged.
    """
    user_secret_manager.create_or_update_secrets(user_id=current_user.id, secrets=user_secrets)
    user_secret_names = user_secret_manager.get_secret_names(current_user.id)
    return UserSecretsResponse(message="Secrets updated successfully", data=user_secret_names)
