import logging
from http import HTTPStatus

from fastapi import HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from openai import AuthenticationError as OpenAIAuthenticationError
from pydantic import ValidationError

logger = logging.getLogger(__name__)


def pydantic_validation_error_handler(request: Request, exc: ValidationError) -> JSONResponse:
    # Log the exception for debugging purposes
    logger.exception(f"request: {request} exc: {exc}")
    error_message = ", ".join([f"{error['loc']}: {error['msg']}" for error in exc.errors()])
    return JSONResponse(
        status_code=HTTPStatus.BAD_REQUEST,
        content={"data": {"message": f"Validation error: {error_message}"}},
    )


def request_validation_error_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    # Log the exception for debugging purposes
    logger.exception(f"request: {request} exc: {exc}")
    error_message = ", ".join([f"{error['loc']}: {error['msg']}" for error in exc.errors()])
    return JSONResponse(
        status_code=HTTPStatus.UNPROCESSABLE_ENTITY,
        content={"data": {"message": f"Validation error: {error_message}"}},
    )


def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    # Log the exception for debugging purposes
    logger.warning(f"request: {request} exc: {exc}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"data": {"message": exc.detail}},
    )


def openai_authentication_error_handler(request: Request, exc: OpenAIAuthenticationError) -> JSONResponse:
    # Log the exception for debugging purposes
    logger.exception(f"request: {request} exc: {exc}")
    return JSONResponse(
        status_code=HTTPStatus.UNAUTHORIZED,
        content={"data": {"message": exc.message}},
    )


def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    # Log the exception for debugging purposes
    logger.exception(f"request: {request} exc: {exc}")
    return JSONResponse(
        status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
        content={"data": {"message": "Internal server error"}},
    )
