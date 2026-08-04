"""
Global exception handlers for FastAPI application.
Provides consistent error response formatting across all endpoints.
"""

import logging
from typing import Union

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from app.exceptions import (
    AMIPError,
    ValidationError,
    DatabaseError,
    AudioError,
    PipelineError,
    StorageError,
    ExportError,
)

logger = logging.getLogger(__name__)


def register_exception_handlers(app: FastAPI) -> None:
    """Register all global exception handlers with FastAPI app.
    
    Args:
        app: FastAPI application instance
    """
    app.add_exception_handler(ValidationError, validation_exception_handler)
    app.add_exception_handler(DatabaseError, database_exception_handler)
    app.add_exception_handler(AudioError, audio_exception_handler)
    app.add_exception_handler(PipelineError, pipeline_exception_handler)
    app.add_exception_handler(StorageError, storage_exception_handler)
    app.add_exception_handler(ExportError, export_exception_handler)
    app.add_exception_handler(AMIPError, amip_exception_handler)
    app.add_exception_handler(Exception, generic_exception_handler)


async def validation_exception_handler(
    request: Request, exc: ValidationError
) -> JSONResponse:
    """Handle validation errors.
    
    Args:
        request: HTTP request
        exc: Validation exception
        
    Returns:
        JSON response with error details
    """
    logger.warning(f"Validation error: {exc.message}")
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "status": "error",
            "code": "VALIDATION_ERROR",
            "detail": exc.message,
            "details": exc.details,
        },
    )


async def database_exception_handler(
    request: Request, exc: DatabaseError
) -> JSONResponse:
    """Handle database errors.
    
    Args:
        request: HTTP request
        exc: Database exception
        
    Returns:
        JSON response with error details
    """
    logger.error(f"Database error: {exc.message}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "status": "error",
            "code": "DATABASE_ERROR",
            "detail": exc.message,
            "details": exc.details,
        },
    )


async def audio_exception_handler(
    request: Request, exc: AudioError
) -> JSONResponse:
    """Handle audio processing errors.
    
    Args:
        request: HTTP request
        exc: Audio exception
        
    Returns:
        JSON response with error details
    """
    logger.error(f"Audio error: {exc.message}")
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "status": "error",
            "code": "AUDIO_ERROR",
            "detail": exc.message,
            "details": exc.details,
        },
    )


async def pipeline_exception_handler(
    request: Request, exc: PipelineError
) -> JSONResponse:
    """Handle pipeline processing errors.
    
    Args:
        request: HTTP request
        exc: Pipeline exception
        
    Returns:
        JSON response with error details
    """
    logger.error(f"Pipeline error: {exc.message}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "status": "error",
            "code": "PIPELINE_ERROR",
            "detail": exc.message,
            "details": exc.details,
        },
    )


async def storage_exception_handler(
    request: Request, exc: StorageError
) -> JSONResponse:
    """Handle storage operation errors.
    
    Args:
        request: HTTP request
        exc: Storage exception
        
    Returns:
        JSON response with error details
    """
    logger.error(f"Storage error: {exc.message}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "status": "error",
            "code": "STORAGE_ERROR",
            "detail": exc.message,
            "details": exc.details,
        },
    )


async def export_exception_handler(
    request: Request, exc: ExportError
) -> JSONResponse:
    """Handle export operation errors.
    
    Args:
        request: HTTP request
        exc: Export exception
        
    Returns:
        JSON response with error details
    """
    logger.error(f"Export error: {exc.message}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "status": "error",
            "code": "EXPORT_ERROR",
            "detail": exc.message,
            "details": exc.details,
        },
    )


async def amip_exception_handler(
    request: Request, exc: AMIPError
) -> JSONResponse:
    """Handle generic AMIP errors.
    
    Args:
        request: HTTP request
        exc: AMIP exception
        
    Returns:
        JSON response with error details
    """
    logger.error(f"AMIP error: {exc.message}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "status": "error",
            "code": "AMIP_ERROR",
            "detail": exc.message,
            "details": exc.details,
        },
    )


async def generic_exception_handler(
    request: Request, exc: Exception
) -> JSONResponse:
    """Handle unexpected exceptions.
    
    Args:
        request: HTTP request
        exc: Unexpected exception
        
    Returns:
        JSON response with error details
    """
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "status": "error",
            "code": "INTERNAL_ERROR",
            "detail": "An unexpected error occurred",
            "details": str(exc),
        },
    )
