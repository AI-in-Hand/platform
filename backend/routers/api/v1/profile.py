from typing import Annotated

from fastapi import APIRouter, Depends, Body

from backend.dependencies.auth import get_current_user
from backend.dependencies.dependencies import get_user_profile_manager
from backend.models.auth import User
from backend.models.response_models import UserProfileResponse
from backend.services.user_profile_manager import UserProfileManager

profile_router = APIRouter(tags=["user"])


@profile_router.get("/user/profile")
async def get_user_profile(
        current_user: Annotated[User, Depends(get_current_user)],
        user_profile_manager: UserProfileManager = Depends(get_user_profile_manager),
) -> UserProfileResponse:
    """
    Retrieve profile data associated with the current user.
    This endpoint fetches profile data stored for the authenticated user.
    """
    user_profile = user_profile_manager.get_user_profile(current_user.id)
    return UserProfileResponse(data=user_profile)


@profile_router.put("/user/profile")
async def update_user_profile(
    current_user: Annotated[User, Depends(get_current_user)],
    user_profile_fields: dict[str, str] = Body(...),
    user_profile_manager: UserProfileManager = Depends(get_user_profile_manager),
) -> UserProfileResponse:
    """
    Update or set profile data associated with the current user.

    This endpoint allows for updating the user's profile data.
    """
    user_profile_manager.update_user_profile(user_id=current_user.id, fields=user_profile_fields)
    user_profile = user_profile_manager.get_user_profile(current_user.id)
    return UserProfileResponse(message="Profile is updated successfully", data=user_profile)
