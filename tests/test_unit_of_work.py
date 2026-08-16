"""Tests for transaction ownership and the SQLAlchemy unit of work."""

import pytest
from sqlalchemy.orm import sessionmaker

from app.database.meeting_repository import MeetingRepository
from app.database.unit_of_work import SqlAlchemyUnitOfWork
from app.models.meeting import Meeting


def test_repository_create_flushes_without_committing(db_session, monkeypatch):
    """Repositories must never commit independently of the service layer."""
    repository = MeetingRepository(db_session)

    def unexpected_commit() -> None:
        raise AssertionError("repository attempted to commit")

    monkeypatch.setattr(db_session, "commit", unexpected_commit)
    meeting = repository.create(Meeting(title="Staged meeting"))

    assert meeting.id is not None


def test_unit_of_work_commits_changes_visible_to_new_session(db_session):
    """A successful unit of work must persist data beyond its original session."""
    session_factory = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=db_session.get_bind(),
    )
    uow = SqlAlchemyUnitOfWork(db_session)

    with uow.transaction():
        meeting = uow.meetings.create(Meeting(title="Committed meeting"))

    meeting_id = meeting.id
    db_session.close()

    verification_session = session_factory()
    try:
        persisted = verification_session.query(Meeting).filter(Meeting.id == meeting_id).one()
        assert persisted.title == "Committed meeting"
    finally:
        verification_session.close()


def test_unit_of_work_rolls_back_staged_changes_on_failure(db_session):
    """Any exception inside the unit of work must rollback all staged changes."""
    uow = SqlAlchemyUnitOfWork(db_session)

    with pytest.raises(RuntimeError, match="forced failure"):
        with uow.transaction():
            uow.meetings.create(Meeting(title="Rolled back meeting"))
            raise RuntimeError("forced failure")

    assert db_session.query(Meeting).count() == 0
