"""
Tests for MeetingService.
"""

import pytest
from datetime import datetime

from app.models.meeting import Meeting
from app.schemas.meeting import MeetingCreate, MeetingUpdate
from app.services.meeting_service import MeetingService


class TestMeetingService:
    """Tests for MeetingService."""
    
    @pytest.fixture
    def service(self, db_session):
        """Create service instance.
        
        Args:
            db_session: Database session fixture
            
        Returns:
            MeetingService instance
        """
        return MeetingService(db_session)
    
    def test_create_meeting(self, service, sample_meeting):
        """Test creating a new meeting.
        
        Verifies that a meeting can be created with valid data.
        """
        # Arrange
        meeting_create = MeetingCreate(**sample_meeting)
        
        # Act
        meeting = service.create(meeting_create)
        
        # Assert
        assert meeting.id is not None
        assert meeting.title == sample_meeting["title"]
        assert meeting.description == sample_meeting["description"]
        assert meeting.created_at is not None
        assert meeting.updated_at is not None
        assert meeting.deleted_at is None
    
    def test_create_meeting_invalid_title(self, service):
        """Test creating a meeting with invalid title.
        
        Verifies that creating a meeting with a short title raises pydantic ValidationError.
        """
        from pydantic import ValidationError
        # Arrange
        with pytest.raises(ValidationError):
            MeetingCreate(title="Ab", description="Test")
    
    def test_get_all_meetings(self, service, sample_meeting):
        """Test retrieving all meetings.
        
        Verifies that meetings can be retrieved with pagination.
        """
        # Arrange
        meeting_create = MeetingCreate(**sample_meeting)
        service.create(meeting_create)
        service.create(meeting_create)
        
        # Act
        meetings = service.get_all(skip=0, limit=10)
        
        # Assert
        assert len(meetings) == 2
        assert all(isinstance(m, Meeting) for m in meetings)
    
    def test_get_meeting_by_id(self, service, sample_meeting):
        """Test retrieving a meeting by ID.
        
        Verifies that a meeting can be retrieved by its ID.
        """
        # Arrange
        meeting_create = MeetingCreate(**sample_meeting)
        created_meeting = service.create(meeting_create)
        
        # Act
        retrieved_meeting = service.get_by_id(created_meeting.id)
        
        # Assert
        assert retrieved_meeting is not None
        assert retrieved_meeting.id == created_meeting.id
        assert retrieved_meeting.title == sample_meeting["title"]
    
    def test_get_meeting_by_id_not_found(self, service):
        """Test retrieving a non-existent meeting.
        
        Verifies that None is returned for non-existent meeting.
        """
        # Act
        meeting = service.get_by_id(999)
        
        # Assert
        assert meeting is None
    
    def test_update_meeting(self, service, sample_meeting, sample_meeting_update):
        """Test updating a meeting.
        
        Verifies that a meeting can be updated with new data.
        """
        # Arrange
        meeting_create = MeetingCreate(**sample_meeting)
        created_meeting = service.create(meeting_create)
        update_data = MeetingUpdate(**sample_meeting_update)
        
        # Act
        updated_meeting = service.update(created_meeting.id, update_data)
        
        # Assert
        assert updated_meeting is not None
        assert updated_meeting.title == sample_meeting_update["title"]
        assert updated_meeting.description == sample_meeting_update["description"]
    
    def test_update_meeting_not_found(self, service, sample_meeting_update):
        """Test updating a non-existent meeting.
        
        Verifies that None is returned when updating non-existent meeting.
        """
        # Arrange
        update_data = MeetingUpdate(**sample_meeting_update)
        
        # Act
        updated_meeting = service.update(999, update_data)
        
        # Assert
        assert updated_meeting is None
    
    def test_delete_meeting(self, service, sample_meeting):
        """Test soft deleting a meeting.
        
        Verifies that a meeting can be soft deleted.
        """
        # Arrange
        meeting_create = MeetingCreate(**sample_meeting)
        created_meeting = service.create(meeting_create)
        
        # Act
        deleted = service.delete(created_meeting.id)
        
        # Assert
        assert deleted is True
        
        # Verify meeting is not returned in active meetings
        active_meetings = service.get_all()
        assert len(active_meetings) == 0
    
    def test_delete_meeting_not_found(self, service):
        """Test soft deleting a non-existent meeting.
        
        Verifies that False is returned when deleting non-existent meeting.
        """
        # Act
        deleted = service.delete(999)
        
        # Assert
        assert deleted is False
    
    def test_count_meetings(self, service, sample_meeting):
        """Test counting meetings.
        
        Verifies that the count reflects active meetings.
        """
        # Arrange
        meeting_create = MeetingCreate(**sample_meeting)
        service.create(meeting_create)
        service.create(meeting_create)
        
        # Act
        count = service.count()
        
        # Assert
        assert count == 2
