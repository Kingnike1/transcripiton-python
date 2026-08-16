"""Global exception handlers with sanitized public responses."""

import logging

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.request_context import get_request_id
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


def register_exception_handlers(app: FastAPI) -> None:
    """Register exception handlers from most specific to most general."""
    app.add_exception_handler(RequestValidationError, request_validation_exception_handler)
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(ValidationError, validation_exception_handler)
    app.add_exception_handler(DatabaseError, database_exception_handler)
    app.add_exception_handler(AudioUploadError, audio_upload_exception_handler)
    app.add_exception_handler(AudioError, audio_exception_handler)
    app.add_exception_handler(PipelineError, pipeline_exception_handler)
    app.add_exception_handler(StorageError, storage_exception_handler)
    app.add_exception_handler(ExportError, export_exception_handler)
    app.add_exception_handler(AMIPError, amip_exception_handler)
    app.add_exception_handler(Exception, generic_exception_handler)


def _error_response(
    request: Request,
    *,
    status_code: int,
    code: str,
    detail: str,
) -> JSONResponse:
    """Build the only public error envelope used by application handlers."""
    return JSONResponse(
        status_code=status_code,
        content={
            "status": "error",
            "code": code,
            "detail": detail,
            "request_id": get_request_id(request),
        },
    )


def _log_context(request: Request) -> dict[str, str]:
    return {"request_id": get_request_id(request)}


async def request_validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """Hide raw request payload/validation internals from the public response."""
    logger.warning(
        "Request validation failed: %s",
        exc.errors(),
        extra=_log_context(request),
    )
    return _error_response(
        request,
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        code="REQUEST_VALIDATION_ERROR",
        detail="Request validation failed",
    )


async def http_exception_handler(
    request: Request, exc: StarletteHTTPException
) -> JSONResponse:
    """Normalize explicit HTTP errors while preserving safe string details."""
    public_detail = exc.detail if isinstance(exc.detail, str) else "Request failed"
    return _error_response(
        request,
        status_code=exc.status_code,
        code=HTTP_ERROR_CODES.get(exc.status_code, f"HTTP_{exc.status_code}"),
        detail=public_detail,
    )


async def validation_exception_handler(
    request: Request, exc: ValidationError
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
    request: Request, exc: DatabaseError
) -> JSONResponse:
    logger.error(
        "Database error: %s; internal_details=%s",
        exc.message,
        exc.details,
        extra=_log_context(request),
        exc_info=True,
    )
    return _error_response(
        request,
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        code="DATABASE_ERROR",
        detail="A database operation failed",
    )


async def audio_upload_exception_handler(
    request: Request, exc: AudioUploadError
) -> JSONResponse:
    """Upload/format messages are validation feedback and safe to expose."""
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


async def audio_exception_handler(
    request: Request, exc: AudioError
) -> JSONResponse:
    logger.error(
        "Audio error: %s; internal_details=%s",
        exc.message,
        exc.details,
        extra=_log_context(request),
        exc_info=True,
    )
    return _error_response(
        request,
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        code="AUDIO_ERROR",
        detail="An audio operation failed",
    )


async def pipeline_exception_handler(
    request: Request, exc: PipelineError
) -> JSONResponse:
    logger.error(
        "Pipeline error: %s; internal_details=%s",
        exc.message,
        exc.details,
        extra=_log_context(request),
        exc_info=True,
    )
    return _error_response(
        request,
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        code="PIPELINE_ERROR",
        detail="Meeting processing failed",
    )


async def storage_exception_handler(
    request: Request, exc: StorageError
) -> JSONResponse:
    logger.error(
        "Storage error: %s; internal_details=%s",
        exc.message,
        exc.details,
        extra=_log_context(request),
        exc_info=True,
    )
    return _error_response(
        request,
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        code="STORAGE_ERROR",
        detail="A storage operation failed",
    )


async def export_exception_handler(
    request: Request, exc: ExportError
) -> JSONResponse:
    logger.error(
        "Export error: %s; internal_details=%s",
        exc.message,
        exc.details,
        extra=_log_context(request),
        exc_info=True,
    )
    return _error_response(
        request,
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        code="EXPORT_ERROR",
        detail="Export generation failed",
    )


async def amip_exception_handler(
    request: Request, exc: AMIPError
) -> JSONResponse:
    logger.error(
        "AMIP error: %s; internal_details=%s",
        exc.message,
        exc.details,
        extra=_log_context(request),
        exc_info=True,
    )
    return _error_response(
        request,
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        code="AMIP_ERROR",
        detail="The requested operation failed",
    )


async def generic_exception_handler(
    request: Request, exc: Exception
) -> JSONResponse:
    """Never expose exception strings, paths, SQL, credentials, or SDK details."""
    logger.exception(
        "Unhandled exception",
        extra=_log_context(request),
    )
    return _error_response(
        request,
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        code="INTERNAL_ERROR",
        detail="An unexpected error occurred",
    )
