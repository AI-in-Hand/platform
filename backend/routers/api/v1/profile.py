import json
import os
from typing import Annotated

from fastapi import APIRouter, Depends, Body
from jsonref import requests

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
    user_profile_data = {}
    if user_profile is not None:
        user_profile_data = {
            "first_name": user_profile.get('first_name'),
            "last_name": user_profile.get('last_name'),
            "email_subscription":
                user_profile.get('email_subscription') if user_profile.get('email_subscription') is not None else "",
        }

    return UserProfileResponse(data=user_profile_data)


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
    user_profile = user_profile_manager.get_user_profile(current_user.id)

    previous_email_subscribe_value = user_profile.get('email_subscription') if user_profile is not None else ""
    requested_email_subscribe_value = user_profile_fields.get("email_subscription")
    if requested_email_subscribe_value and (previous_email_subscribe_value != requested_email_subscribe_value):
        api_key = os.environ.get('MAILCHIMP_API_KEY')
        list_id = os.environ.get('MAILCHIMP_LIST_ID')
        email = current_user.email
        # Data to send in the request
        data = {
            "email_address": email,
            "status": requested_email_subscribe_value
        }
        # Headers for the request
        headers = {
            'Authorization': f'apikey {api_key}',
            'Content-Type': 'application/json'
        }
        mailchimp_member_hash_id = user_profile.get('mail_chimp_member_hash_id') if user_profile is not None else ""
        if mailchimp_member_hash_id:
            # Mailchimp API URL
            url = f'https://<dc>.api.mailchimp.com/3.0/lists/{list_id}/members/{mailchimp_member_hash_id}'
            # Replace <dc> with your data center prefix (e.g., 'us5')
            url = url.replace('<dc>', api_key.split('-')[-1])

            requests.put(url, headers=headers, data=json.dumps(data))

        else:
            # Mailchimp API URL
            url = f'https://<dc>.api.mailchimp.com/3.0/lists/{list_id}/members/'
            # Replace <dc> with your data center prefix (e.g., 'us5')
            url = url.replace('<dc>', api_key.split('-')[-1])

            response = requests.post(url, headers=headers, data=json.dumps(data))
            if response.status_code == 200:
                member_id = response.json().get('id')
                user_profile_fields["mail_chimp_member_hash_id"] = member_id

    user_profile_manager.update_user_profile(user_id=current_user.id, fields=user_profile_fields)
    user_profile = user_profile_manager.get_user_profile(current_user.id)
    user_profile_data = {
        "first_name": user_profile.get('first_name'),
        "last_name": user_profile.get('last_name'),
        "email_subscription":
            user_profile.get('email_subscription') if user_profile.get('email_subscription') is not None else "",
    }

    return UserProfileResponse(message="Profile is updated successfully", data=user_profile_data)
