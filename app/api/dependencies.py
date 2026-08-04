"""
Dependency injection module for AMIP.
Provides dependencies for FastAPI routes.
"""

from typing import Generator
from fastapi import Depends
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.services.meeting_service import MeetingService


def get_meeting_service(db: Session = Depends(get_db)) -> MeetingService:
    """Get meeting service instance.
    
    Args:
        db: Database session
        
    Returns:
        MeetingService instance
    """
    return MeetingService(db)
