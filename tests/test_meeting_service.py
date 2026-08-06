"""Tests for MeetingService."""

import pytest
from sqlalchemy.orm import sessionmaker

from app.core.enums import ProcessingStatus
from app.models.meeting import Meeting
from app.schemas.meeting import MeetingCreate, MeetingUpdate
from app.services.meeting_service import MeetingService


class TestMeetingService:
    """Tests for meeting business logic and transaction boundaries."""

    @pytest.fixture
    def service(self, db_session):
        """Create a service instance for the current test session."""
        return MeetingService(db_session)

    def test_create_meeting(self, service, sample_meeting):
        meeting = service.create(MeetingCreate(**sample_meeting))

        assert meeting.id is not None
        assert meeting.title == sample_meeting["title"]
        assert meeting.description == sample_meeting["description"]
        assert meeting.created_at is not None
        assert meeting.updated_at is not None
        assert meeting.deleted_at is None

    def test_create_meeting_invalid_title(self, service):
        from pydantic import ValidationError

        with pytest.raises(ValidationError):
            MeetingCreate(title="Ab", description="Test")

    def test_get_all_meetings(self, service, sample_meeting):
        meeting_create = MeetingCreate(**sample_meeting)
        service.create(meeting_create)
        service.create(meeting_create)

        meetings = service.get_all(skip=0, limit=10)

        assert len(meetings) == 2
        assert all(isinstance(meeting, Meeting) for meeting in meetings)

    def test_get_meeting_by_id(self, service, sample_meeting):
        created_meeting = service.create(MeetingCreate(**sample_meeting))

        retrieved_meeting = service.get_by_id(created_meeting.id)

        assert retrieved_meeting is not None
        assert retrieved_meeting.id == created_meeting.id
        assert retrieved_meeting.title == sample_meeting["title"]

    def test_get_meeting_by_id_not_found(self, service):
        assert service.get_by_id(999) is None

    def test_update_meeting(self, service, sample_meeting, sample_meeting_update):
        created_meeting = service.create(MeetingCreate(**sample_meeting))
        update_data = MeetingUpdate(**sample_meeting_update)

        updated_meeting = service.update(created_meeting.id, update_data)

        assert updated_meeting is not None
        assert updated_meeting.title == sample_meeting_update["title"]
        assert updated_meeting.description == sample_meeting_update["description"]

    def test_update_meeting_not_found(self, service, sample_meeting_update):
        update_data = MeetingUpdate(**sample_meeting_update)

        assert service.update(999, update_data) is None

    def test_delete_meeting(self, service, sample_meeting):
        created_meeting = service.create(MeetingCreate(**sample_meeting))

        deleted = service.delete(created_meeting.id)

        assert deleted is True
        assert service.get_all() == []

    def test_delete_meeting_not_found(self, service):
        assert service.delete(999) is False

    def test_count_meetings(self, service, sample_meeting):
        meeting_create = MeetingCreate(**sample_meeting)
        service.create(meeting_create)
        service.create(meeting_create)

        assert service.count() == 2

    def test_transition_status_persists_in_new_session(self, db_session, sample_meeting):
        """A committed transition must survive closing the original session."""
        service = MeetingService(db_session)
        meeting = service.create(MeetingCreate(**sample_meeting))
        meeting_id = meeting.id
        bind = db_session.get_bind()
        verification_factory = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=bind,
        )

        assert service.transition_status(meeting_id, ProcessingStatus.AUDIO_UPLOADED)
        db_session.close()

        verification_session = verification_factory()
        try:
            persisted = (
                verification_session.query(Meeting)
                .filter(Meeting.id == meeting_id)
                .one()
            )
            assert persisted.status == ProcessingStatus.AUDIO_UPLOADED.value
        finally:
            verification_session.close()

    def test_invalid_transition_is_not_persisted(self, service, sample_meeting):
        """Invalid state changes must leave the persisted status untouched."""
        meeting = service.create(MeetingCreate(**sample_meeting))

        changed = service.transition_status(meeting.id, ProcessingStatus.COMPLETED)
        service.uow.session.expire_all()
        persisted = service.get_by_id(meeting.id)

        assert changed is False
        assert persisted is not None
        assert persisted.status == ProcessingStatus.CREATED.value

    def test_create_rolls_back_when_commit_fails(
        self, service, db_session, sample_meeting, monkeypatch
    ):
        """A service-level commit failure must rollback staged repository data."""

        def fail_commit() -> None:
            raise RuntimeError("commit unavailable")

        monkeypatch.setattr(service.uow, "commit", fail_commit)

        with pytest.raises(RuntimeError, match="commit unavailable"):
            service.create(MeetingCreate(**sample_meeting))

        assert db_session.query(Meeting).count() == 0
