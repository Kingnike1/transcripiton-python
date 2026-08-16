"""Global exception handlers with sanitized public responses."""

import logging
from types import TracebackType
from typing import Awaitable, Callable, Optional, cast

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.responses import Response

from app.core.request_context import REQUEST_ID_HEADER, get_request_id
from app.exceptions import (
    AMIPError,
    AudioError,
    AudioUploadError,
    DatabaseError,
    ExportError,
    PipelineError,
    StorageError,
    ValidationError,
)

logger = logging.getLogger(__name__)

HTTP_ERROR_CODES = {
    400: "BAD_REQUEST",
    401: "UNAUTHORIZED",
    403: "FORBIDDEN",
    404: "NOT_FOUND",
    409: "CONFLICT",
    413: "PAYLOAD_TOO_LARGE",
    415: "UNSUPPORTED_MEDIA_TYPE",
    422: "REQUEST_VALIDATION_ERROR",
    429: "RATE_LIMITED",
    503: "SERVICE_UNAVAILABLE",
}

StarletteExceptionHandler = Callable[[Request, Exception], Response | Awaitable[Response]]


def _starlette_handler(handler: Callable[..., Awaitable[JSONResponse]]) -> StarletteExceptionHandler:
    """Adapt typed handlers to Starlette's intentionally generic handler signature."""
    return cast(StarletteExceptionHandler, handler)


def register_exception_handlers(app: FastAPI) -> None:
    """Register handlers from most specific to most general."""
    app.add_exception_handler(
        RequestValidationError,
        _starlette_handler(request_validation_exception_handler),
    )
    app.add_exception_handler(
        StarletteHTTPException,
        _starlette_handler(http_exception_handler),
    )
    app.add_exception_handler(
        ValidationError,
        _starlette_handler(validation_exception_handler),
    )
    app.add_exception_handler(
        DatabaseError,
        _starlette_handler(database_exception_handler),
    )
    app.add_exception_handler(
        AudioUploadError,
        _starlette_handler(audio_upload_exception_handler),
    )
    app.add_exception_handler(AudioError, _starlette_handler(audio_exception_handler))
    app.add_exception_handler(PipelineError, _starlette_handler(pipeline_exception_handler))
    app.add_exception_handler(StorageError, _starlette_handler(storage_exception_handler))
    app.add_exception_handler(ExportError, _starlette_handler(export_exception_handler))
    app.add_exception_handler(AMIPError, _starlette_handler(amip_exception_handler))
    app.add_exception_handler(Exception, _starlette_handler(generic_exception_handler))


def _error_response(
    request: Request,
    *,
    status_code: int,
    code: str,
    detail: str,
) -> JSONResponse:
    """Build the public error envelope without exposing internal details."""
    request_id = get_request_id(request)
    return JSONResponse(
        status_code=status_code,
        content={
            "status": "error",
            "code": code,
            "detail": detail,
            "request_id": request_id,
        },
        headers={REQUEST_ID_HEADER: request_id},
    )


def _log_context(request: Request) -> dict[str, str]:
    return {"request_id": get_request_id(request)}


def _exc_info(
    exc: BaseException,
) -> tuple[type[BaseException], BaseException, Optional[TracebackType]]:
    """Preserve a received traceback even outside an active ``except`` block."""
    return (type(exc), exc, exc.__traceback__)


async def request_validation_exception_handler(
    request: Request,
    exc: RequestValidationError,
) -> JSONResponse:
    logger.warning(
        "Request validation failed: %s",
        exc.errors(),
        extra=_log_context(request),
    )
    return _error_response(
        request,
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        code="REQUEST_VALIDATION_ERROR",
        detail="Request validation failed",
    )


async def http_exception_handler(
    request: Request,
    exc: StarletteHTTPException,
) -> JSONResponse:
    public_detail = exc.detail if isinstance(exc.detail, str) else "Request failed"
    return _error_response(
        request,
        status_code=exc.status_code,
        code=HTTP_ERROR_CODES.get(exc.status_code, f"HTTP_{exc.status_code}"),
        detail=public_detail,
    )


async def validation_exception_handler(
    request: Request,
    exc: ValidationError,
) -> JSONResponse:
    logger.warning(
        "Validation error: %s; internal_details=%s",
        exc.message,
        exc.details,
        extra=_log_context(request),
    )
    return _error_response(
        request,
        status_code=status.HTTP_400_BAD_REQUEST,
        code="VALIDATION_ERROR",
        detail=exc.message,
    )


async def database_exception_handler(
    request: Request,
    exc: DatabaseError,
) -> JSONResponse:
    logger.error(
        "Database error: %s; internal_details=%s",
        exc.message,
        exc.details,
        extra=_log_context(request),
        exc_info=_exc_info(exc),
    )
    return _error_response(
        request,
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        code="DATABASE_ERROR",
        detail="A database operation failed",
    )


async def audio_upload_exception_handler(
    request: Request,
    exc: AudioUploadError,
) -> JSONResponse:
    logger.warning(
        "Audio upload rejected: %s; internal_details=%s",
        exc.message,
        exc.details,
        extra=_log_context(request),
    )
    return _error_response(
        request,
        status_code=status.HTTP_400_BAD_REQUEST,
        code="AUDIO_UPLOAD_ERROR",
        detail=exc.message,
    )


async def audio_exception_handler(request: Request, exc: AudioError) -> JSONResponse:
    logger.error(
        "Audio error: %s; internal_details=%s",
        exc.message,
        exc.details,
        extra=_log_context(request),
        exc_info=_exc_info(exc),
    )
    return _error_response(
        request,
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        code="AUDIO_ERROR",
        detail="An audio operation failed",
    )


async def pipeline_exception_handler(request: Request, exc: PipelineError) -> JSONResponse:
    logger.error(
        "Pipeline error: %s; internal_details=%s",
        exc.message,
        exc.details,
        extra=_log_context(request),
        exc_info=_exc_info(exc),
    )
    return _error_response(
        request,
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        code="PIPELINE_ERROR",
        detail="Meeting processing failed",
    )


async def storage_exception_handler(request: Request, exc: StorageError) -> JSONResponse:
    logger.error(
        "Storage error: %s; internal_details=%s",
        exc.message,
        exc.details,
        extra=_log_context(request),
        exc_info=_exc_info(exc),
    )
    return _error_response(
        request,
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        code="STORAGE_ERROR",
        detail="A storage operation failed",
    )


async def export_exception_handler(request: Request, exc: ExportError) -> JSONResponse:
    logger.error(
        "Export error: %s; internal_details=%s",
        exc.message,
        exc.details,
        extra=_log_context(request),
        exc_info=_exc_info(exc),
    )
    return _error_response(
        request,
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        code="EXPORT_ERROR",
        detail="Export generation failed",
    )


async def amip_exception_handler(request: Request, exc: AMIPError) -> JSONResponse:
    logger.error(
        "AMIP error: %s; internal_details=%s",
        exc.message,
        exc.details,
        extra=_log_context(request),
        exc_info=_exc_info(exc),
    )
    return _error_response(
        request,
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        code="AMIP_ERROR",
        detail="The requested operation failed",
    )


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Never expose exception strings, paths, SQL, credentials, or SDK details."""
    logger.error(
        "Unhandled exception",
        extra=_log_context(request),
        exc_info=_exc_info(exc),
    )
    return _error_response(
        request,
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        code="INTERNAL_ERROR",
        detail="An unexpected error occurred",
    )
