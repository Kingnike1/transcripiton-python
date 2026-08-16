"""Integration tests for Alembic schema management."""

import os
from pathlib import Path
import subprocess
import sys

from alembic.autogenerate import compare_metadata
from alembic.migration import MigrationContext
from sqlalchemy import create_engine, inspect, text

from app.database.base import Base
import app.models  # noqa: F401 - register mapped models

PROJECT_ROOT = Path(__file__).resolve().parents[1]
BUSINESS_TABLES = {
    "meetings",
    "audios",
    "transcriptions",
    "speaker_segments",
    "meeting_analysis",
    "processing_jobs",
}


def _run_alembic(database_url: str, *args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env["DATABASE_URL"] = database_url
    return subprocess.run(
        [sys.executable, "-m", "alembic", "-c", "alembic.ini", *args],
        cwd=PROJECT_ROOT,
        env=env,
        text=True,
        capture_output=True,
        check=check,
    )


def _schema_differences(database_url: str):
    engine = create_engine(database_url)
    try:
        with engine.connect() as connection:
            context = MigrationContext.configure(connection)
            return compare_metadata(context, Base.metadata)
    finally:
        engine.dispose()


def test_upgrade_head_matches_sqlalchemy_metadata(tmp_path):
    database_path = tmp_path / "migration.db"
    database_url = f"sqlite:///{database_path}"
    _run_alembic(database_url, "upgrade", "head")

    engine = create_engine(database_url)
    try:
        inspector = inspect(engine)
        table_names = set(inspector.get_table_names())
        audio_indexes = {index["name"] for index in inspector.get_indexes("audios")}
        job_indexes = {index["name"] for index in inspector.get_indexes("processing_jobs")}
        assert BUSINESS_TABLES.issubset(table_names)
        assert "alembic_version" in table_names
        assert "uq_audios_active_meeting" in audio_indexes
        assert "uq_processing_jobs_active_meeting_type" in job_indexes
        assert "ix_processing_jobs_status_available" in job_indexes
    finally:
        engine.dispose()

    assert _schema_differences(database_url) == []


def test_pre_alembic_baseline_is_stamped_then_upgraded(tmp_path):
    database_path = tmp_path / "legacy.db"
    database_url = f"sqlite:///{database_path}"
    _run_alembic(database_url, "upgrade", "0001_initial_schema")
    engine = create_engine(database_url)
    try:
        with engine.begin() as connection:
            connection.execute(text("DROP TABLE alembic_version"))
    finally:
        engine.dispose()
    _run_alembic(database_url, "stamp", "0001_initial_schema")
    _run_alembic(database_url, "upgrade", "head")
    assert _schema_differences(database_url) == []


def test_current_matching_schema_can_be_stamped_at_head(tmp_path):
    database_path = tmp_path / "current-legacy.db"
    database_url = f"sqlite:///{database_path}"
    engine = create_engine(database_url)
    try:
        Base.metadata.create_all(bind=engine)
    finally:
        engine.dispose()
    _run_alembic(database_url, "stamp", "head")
    assert _schema_differences(database_url) == []


def test_active_audio_index_rejects_two_active_rows_but_allows_deleted_history(tmp_path):
    database_path = tmp_path / "integrity.db"
    database_url = f"sqlite:///{database_path}"
    _run_alembic(database_url, "upgrade", "head")
    engine = create_engine(database_url)
    try:
        with engine.begin() as connection:
            connection.execute(text("INSERT INTO meetings (id, title, status, created_at, updated_at) VALUES (1, 'Concurrency', 'CREATED', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)"))
            connection.execute(text("INSERT INTO audios (id, meeting_id, filename, file_path, created_at, updated_at) VALUES (1, 1, 'first.wav', 'audio/1/first.wav', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)"))
        try:
            with engine.begin() as connection:
                connection.execute(text("INSERT INTO audios (id, meeting_id, filename, file_path, created_at, updated_at) VALUES (2, 1, 'second.wav', 'audio/1/second.wav', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)"))
        except Exception as exc:
            assert "UNIQUE constraint failed: audios.meeting_id" in str(exc)
        else:
            raise AssertionError("second active audio unexpectedly satisfied unique index")
        with engine.begin() as connection:
            connection.execute(text("UPDATE audios SET deleted_at = CURRENT_TIMESTAMP WHERE id = 1"))
            connection.execute(text("INSERT INTO audios (id, meeting_id, filename, file_path, created_at, updated_at) VALUES (2, 1, 'replacement.wav', 'audio/1/replacement.wav', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)"))
    finally:
        engine.dispose()


def test_unique_index_migration_refuses_preexisting_duplicate_active_audio(tmp_path):
    database_path = tmp_path / "duplicate.db"
    database_url = f"sqlite:///{database_path}"
    _run_alembic(database_url, "upgrade", "0002_audio_media_metadata")
    engine = create_engine(database_url)
    try:
        with engine.begin() as connection:
            connection.execute(text("INSERT INTO meetings (id, title, status, created_at, updated_at) VALUES (1, 'Duplicate data', 'CREATED', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)"))
            for audio_id in (1, 2):
                connection.execute(
                    text("INSERT INTO audios (id, meeting_id, filename, file_path, created_at, updated_at) VALUES (:id, 1, :filename, :path, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)"),
                    {"id": audio_id, "filename": f"{audio_id}.wav", "path": f"audio/1/{audio_id}.wav"},
                )
    finally:
        engine.dispose()
    result = _run_alembic(database_url, "upgrade", "head", check=False)
    assert result.returncode != 0
    assert "duplicate active audios" in (result.stderr + result.stdout)


def test_processing_job_unique_active_index(tmp_path):
    database_path = tmp_path / "jobs.db"
    database_url = f"sqlite:///{database_path}"
    _run_alembic(database_url, "upgrade", "head")
    engine = create_engine(database_url)
    try:
        with engine.begin() as connection:
            connection.execute(text("INSERT INTO meetings (id, title, status, created_at, updated_at) VALUES (1, 'Jobs', 'AUDIO_UPLOADED', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)"))
            values = "('job-1', 1, 'TRANSCRIBE', 'PENDING', 0, 0, 3, '{}', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)"
            connection.execute(text("INSERT INTO processing_jobs (id, meeting_id, job_type, status, progress, attempt, max_attempts, payload, available_at, created_at, updated_at) VALUES " + values))
        try:
            with engine.begin() as connection:
                values = "('job-2', 1, 'TRANSCRIBE', 'PENDING', 0, 0, 3, '{}', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)"
                connection.execute(text("INSERT INTO processing_jobs (id, meeting_id, job_type, status, progress, attempt, max_attempts, payload, available_at, created_at, updated_at) VALUES " + values))
        except Exception as exc:
            assert "UNIQUE constraint failed" in str(exc)
        else:
            raise AssertionError("second active transcription job unexpectedly satisfied unique index")
    finally:
        engine.dispose()


def test_downgrade_base_removes_business_schema(tmp_path):
    database_path = tmp_path / "migration.db"
    database_url = f"sqlite:///{database_path}"
    _run_alembic(database_url, "upgrade", "head")
    _run_alembic(database_url, "downgrade", "base")
    engine = create_engine(database_url)
    try:
        table_names = set(inspect(engine).get_table_names())
        assert BUSINESS_TABLES.isdisjoint(table_names)
    finally:
        engine.dispose()
