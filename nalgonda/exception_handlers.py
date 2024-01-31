import logging
from http import HTTPStatus

from fastapi import Request
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)


def bad_request_exception_handler(request: Request, exc: ValueError) -> JSONResponse:  # noqa: ARG001
    return JSONResponse(
        status_code=HTTPStatus.BAD_REQUEST,
        content={"detail": str(exc)},
    )
