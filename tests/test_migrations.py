"""Integration tests for Alembic schema management."""

import os
from pathlib import Path
import subprocess
import sys

from alembic.autogenerate import compare_metadata
from alembic.migration import MigrationContext
from sqlalchemy import create_engine, inspect

from app.database.base import Base
import app.models  # noqa: F401 - register mapped models

PROJECT_ROOT = Path(__file__).resolve().parents[1]
BUSINESS_TABLES = {
    "meetings",
    "audios",
    "transcriptions",
    "speaker_segments",
    "meeting_analysis",
}


def _run_alembic(database_url: str, *args: str) -> subprocess.CompletedProcess[str]:
    """Run Alembic in an isolated interpreter with an explicit database URL."""
    env = os.environ.copy()
    env["DATABASE_URL"] = database_url
    return subprocess.run(
        [sys.executable, "-m", "alembic", "-c", "alembic.ini", *args],
        cwd=PROJECT_ROOT,
        env=env,
        text=True,
        capture_output=True,
        check=True,
    )


def _schema_differences(database_url: str):
    """Return Alembic autogenerate differences against current ORM metadata."""
    engine = create_engine(database_url)
    try:
        with engine.connect() as connection:
            context = MigrationContext.configure(connection)
            return compare_metadata(context, Base.metadata)
    finally:
        engine.dispose()


def test_upgrade_head_matches_sqlalchemy_metadata(tmp_path):
    """A fresh database migrated to head must match the ORM schema exactly."""
    database_path = tmp_path / "migration.db"
    database_url = f"sqlite:///{database_path}"

    _run_alembic(database_url, "upgrade", "head")

    engine = create_engine(database_url)
    try:
        table_names = set(inspect(engine).get_table_names())
        assert BUSINESS_TABLES.issubset(table_names)
        assert "alembic_version" in table_names
    finally:
        engine.dispose()

    assert _schema_differences(database_url) == []


def test_existing_schema_can_be_stamped_without_recreating_tables(tmp_path):
    """A matching pre-Alembic database can adopt the baseline with stamp head."""
    database_path = tmp_path / "legacy.db"
    database_url = f"sqlite:///{database_path}"
    engine = create_engine(database_url)
    try:
        Base.metadata.create_all(bind=engine)
    finally:
        engine.dispose()

    _run_alembic(database_url, "stamp", "head")

    engine = create_engine(database_url)
    try:
        table_names = set(inspect(engine).get_table_names())
        assert BUSINESS_TABLES.issubset(table_names)
        assert "alembic_version" in table_names
    finally:
        engine.dispose()

    assert _schema_differences(database_url) == []


def test_downgrade_base_removes_business_schema(tmp_path):
    """The baseline migration must be reversible on a disposable database."""
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
