import logging
from typing import Any

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.utils.logger import get_logger
from app.utils.request_context import get_request_id
from app.utils.responses import build_error_response

logger = get_logger(__name__)


def install_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
        request_id = getattr(request.state, "request_id", get_request_id())
        payload = build_error_response(
            error_code=f"http_{exc.status_code}",
            description=str(exc.detail),
            possible_solution="Review the request payload, authentication headers, or route path.",
            request_id=request_id,
        )
        return JSONResponse(status_code=exc.status_code, content=payload)

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
        request_id = getattr(request.state, "request_id", get_request_id())
        payload = build_error_response(
            error_code="validation_error",
            description="The request payload failed validation.",
            possible_solution="Check the submitted fields, types, and required values.",
            request_id=request_id,
        )
        payload["details"] = exc.errors()
        return JSONResponse(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, content=payload)

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        request_id = getattr(request.state, "request_id", get_request_id())
        logger.exception("Unhandled application error", exc_info=exc)
        payload = build_error_response(
            error_code="internal_server_error",
            description="An unexpected server error occurred.",
            possible_solution="Retry the request or contact the platform team if the issue persists.",
            request_id=request_id,
        )
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content=payload)
