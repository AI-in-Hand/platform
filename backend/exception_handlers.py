import logging
from http import HTTPStatus

from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import ValidationError

logger = logging.getLogger(__name__)


def pydantic_validation_error_handler(request: Request, exc: ValidationError) -> JSONResponse:
    # Log the exception for debugging purposes
    logger.exception(f"request: {request} exc: {exc}")
    return JSONResponse(
        status_code=HTTPStatus.BAD_REQUEST,
        content={"data": {"message": exc.errors()}},
    )


def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    # Log the exception for debugging purposes
    logger.warning(f"request: {request} exc: {exc}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"data": {"message": exc.detail}},
    )


def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    # Log the exception for debugging purposes
    logger.exception(f"request: {request} exc: {exc}")
    return JSONResponse(
        status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
        content={"data": {"message": "Internal server error"}},
    )
