"""Readiness/capability API for operator-safe diagnostics."""

from fastapi import APIRouter

from app.services.readiness_service import ReadinessService

router = APIRouter(prefix="/api/readiness", tags=["readiness"])


@router.get("")
def get_readiness() -> dict[str, object]:
    """Return environment capabilities without exposing secret values."""
    return ReadinessService().payload()
