import logging
from http import HTTPStatus

from fastapi import Request
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)


def bad_request_exception_handler(request: Request, exc: ValueError) -> JSONResponse:
    # Log the exception for debugging purposes
    logger.exception(f"request: {request} exc: {exc}")
    return JSONResponse(
        status_code=HTTPStatus.BAD_REQUEST,
        content={"detail": str(exc)},
    )


def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    # Log the exception for debugging purposes
    logger.exception(f"request: {request} exc: {exc}")
    return JSONResponse(
        status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error"},
    )
