import logging

from fastapi import HTTPException, Request, Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint

from backend.services.auth_service import AuthService
from backend.services.context_vars_manager import ContextEnvVarsManager

logger = logging.getLogger(__name__)


class UserContextMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        token = request.headers.get("Authorization")
        if token:
            token = token.replace("Bearer ", "")
            try:
                user = AuthService.get_user(token)
            except HTTPException:
                user = None
            if user:
                ContextEnvVarsManager.set("user_id", user.id)
                logger.info(f"Current User ID set in context: {user.id}")

        response = await call_next(request)
        return response
