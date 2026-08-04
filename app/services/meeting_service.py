"""
Meeting service module.
Contains business logic for meeting operations.
Uses Repository Pattern for data access.
"""

from datetime import datetime
from typing import List, Optional
from sqlalchemy.orm import Session

from app.core.enums import ProcessingStatus
from app.database.meeting_repository import MeetingRepository
from app.models.meeting import Meeting
from app.schemas.meeting import MeetingCreate, MeetingUpdate


class MeetingService:
    """Service for managing meetings.
    
    Handles all business logic related to meetings including
    creation, retrieval, update, and deletion.
    
    Uses MeetingRepository for all database operations.
    """
    
    def __init__(self, db: Session):
        """Initialize meeting service.
        
        Args:
            db: Database session
        """
        self.repository = MeetingRepository(db)
    
    def create(self, meeting: MeetingCreate) -> Meeting:
        """Create a new meeting.
        
        Args:
            meeting: Meeting creation data
            
        Returns:
            Created Meeting instance
            
        Raises:
            ValueError: If meeting title is invalid
        """
        if not meeting.title or len(meeting.title.strip()) < 3:
            raise ValueError("Meeting title must be at least 3 characters")

        db_meeting = Meeting(
            title=meeting.title.strip(),
            description=meeting.description,
            status=ProcessingStatus.CREATED.value,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        
        return self.repository.create(db_meeting)
    
    def get_all(self, skip: int = 0, limit: int = 10) -> List[Meeting]:
        """Get all active meetings with pagination.
        
        Args:
            skip: Number of records to skip
            limit: Number of records to return
            
        Returns:
            List of Meeting instances
        """
        return self.repository.get_all(skip=skip, limit=limit)
    
    def get_by_id(self, meeting_id: int) -> Optional[Meeting]:
        """Get meeting by ID.
        
        Args:
            meeting_id: Meeting ID
            
        Returns:
            Meeting instance if found, None otherwise
        """
        return self.repository.get_by_id(meeting_id)
    
    def update(self, meeting_id: int, meeting: MeetingUpdate) -> Optional[Meeting]:
        """Update a meeting.
        
        Args:
            meeting_id: Meeting ID to update
            meeting: Meeting update data
            
        Returns:
            Updated Meeting instance if found, None otherwise
        """
        db_meeting = self.get_by_id(meeting_id)
        
        if not db_meeting:
            return None

        update_data = meeting.model_dump(exclude_unset=True)
        
        for key, value in update_data.items():
            setattr(db_meeting, key, value)
            
        db_meeting.updated_at = datetime.utcnow()
        
        return self.repository.update(db_meeting)
    
    def delete(self, meeting_id: int) -> bool:
        """Soft delete a meeting.
        
        Args:
            meeting_id: Meeting ID to delete
            
        Returns:
            True if deleted, False if not found
        """
        return self.repository.delete(meeting_id)
    
    def count(self) -> int:
        """Count total active meetings.
        
        Returns:
            Number of active meetings
        """
        return self.repository.count()
    
    def search(self, query: str, skip: int = 0, limit: int = 10) -> List[Meeting]:
        """Search meetings by title or description.
        
        Args:
            query: Search term
            skip: Number of records to skip
            limit: Number of records to return
            
        Returns:
            List of matching Meeting instances
        """
        return self.repository.search(query, skip=skip, limit=limit)
    
    def count_search(self, query: str) -> int:
        """Count meetings matching search query.
        
        Args:
            query: Search term
            
        Returns:
            Number of matching meetings
        """
        return self.repository.count_search(query)
    
    def transition_status(
        self, meeting_id: int, new_status: ProcessingStatus
    ) -> bool:
        """Transition a meeting to a new processing status.
        
        Args:
            meeting_id: Meeting ID
            new_status: Target processing status
            
        Returns:
            True if transition was applied, False if invalid or not found
        """
        db_meeting = self.get_by_id(meeting_id)
        
        if not db_meeting:
            return False
        
        return db_meeting.transition_status(new_status)
    
    def get_by_status(self, status: ProcessingStatus) -> List[Meeting]:
        """Get meetings by processing status.
        
        Args:
            status: Processing status
            
        Returns:
            List of Meeting instances with given status
        """
        return self.repository.get_by_status(status.value)
