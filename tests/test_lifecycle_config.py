"""Regression tests for P0.6 lifecycle and runtime configuration."""

from datetime import timedelta
import os
from pathlib import Path
import subprocess
import sys

import pytest
from pydantic import ValidationError

from app.config.application import ApplicationSettings
from app.core.enums import ProcessingStatus
from app.core.time import utc_now
from app.database.meeting_repository import MeetingRepository
from app.models.meeting import Meeting

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_importing_main_does_not_create_database_schema(tmp_path):
    """Importing the web app must not connect to SQLite just to create tables."""
    database_path = tmp_path / "import-only.db"
    env = os.environ.copy()
    env.update(
        {
            "DATABASE_URL": f"sqlite:///{database_path}",
            "ENVIRONMENT": "test",
            "DEBUG": "false",
            "SECRET_KEY": "test-secret",
        }
    )

    subprocess.run(
        [sys.executable, "-c", "import main"],
        cwd=PROJECT_ROOT,
        env=env,
        check=True,
        capture_output=True,
        text=True,
    )

    assert not database_path.exists()


def test_production_rejects_debug_mode():
    """Production configuration must never accept debug mode."""
    with pytest.raises(ValidationError, match="DEBUG must be disabled"):
        ApplicationSettings(
            _env_file=None,
            ENVIRONMENT="production",
            DEBUG=True,
            SECRET_KEY="x" * 40,
        )


def test_production_rejects_weak_secret():
    """Production configuration must reject short or placeholder secrets."""
    with pytest.raises(ValidationError, match="SECRET_KEY must contain"):
        ApplicationSettings(
            _env_file=None,
            ENVIRONMENT="production",
            DEBUG=False,
            SECRET_KEY="secret",
        )


def test_production_accepts_safe_runtime_configuration():
    """A production-safe configuration should validate successfully."""
    settings = ApplicationSettings(
        _env_file=None,
        ENVIRONMENT="production",
        DEBUG=False,
        SECRET_KEY="a-secure-production-secret-value-123456789",
    )

    assert settings.ENVIRONMENT == "production"
    assert settings.DEBUG is False


def test_stale_processing_honors_requested_minutes(db_session):
    """Changing the threshold must change which processing rows are stale."""
    now = utc_now()
    old = Meeting(
        title="Old processing",
        status=ProcessingStatus.TRANSCRIBING.value,
        created_at=now - timedelta(minutes=60),
        updated_at=now - timedelta(minutes=40),
    )
    recent = Meeting(
        title="Recent processing",
        status=ProcessingStatus.DIARIZING.value,
        created_at=now - timedelta(minutes=20),
        updated_at=now - timedelta(minutes=10),
    )
    completed = Meeting(
        title="Old completed",
        status=ProcessingStatus.COMPLETED.value,
        created_at=now - timedelta(minutes=60),
        updated_at=now - timedelta(minutes=50),
    )
    db_session.add_all([old, recent, completed])
    db_session.commit()

    repository = MeetingRepository(db_session)

    stale_30 = {meeting.title for meeting in repository.get_stale_processing(30)}
    stale_5 = {meeting.title for meeting in repository.get_stale_processing(5)}

    assert stale_30 == {"Old processing"}
    assert stale_5 == {"Old processing", "Recent processing"}


def test_stale_processing_rejects_non_positive_threshold(db_session):
    """A zero/negative stale threshold is a caller error, not a valid query."""
    repository = MeetingRepository(db_session)

    with pytest.raises(ValueError, match="minutes must be greater than zero"):
        repository.get_stale_processing(0)
