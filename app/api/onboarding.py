"""Onboarding API for the current AMIP workspace."""

from fastapi import APIRouter, Depends

from app.api.dependencies import get_current_user_optional, get_meeting_service
from app.models.user import User
from app.services.meeting_service import MeetingService
from app.services.onboarding_service import OnboardingService
from app.services.readiness_service import ReadinessService

router = APIRouter(prefix="/api/onboarding", tags=["onboarding"])


@router.get("")
def get_onboarding(
    current_user: User | None = Depends(get_current_user_optional),
    meetings: MeetingService = Depends(get_meeting_service),
) -> dict[str, object]:
    """Return a safe guide for the authenticated/local workspace."""
    owner_id = current_user.id if current_user is not None else None
    meeting_count = len(meetings.get_all(skip=0, limit=101, owner_id=owner_id))
    return OnboardingService().build(meeting_count, ReadinessService().payload())
