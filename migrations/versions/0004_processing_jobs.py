"""Add durable processing jobs.

Revision ID: 0004_processing_jobs
Revises: 0003_one_active_audio_per_meeting
Create Date: 2026-08-16
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0004_processing_jobs"
down_revision: Union[str, None] = "0003_one_active_audio_per_meeting"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "processing_jobs",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("meeting_id", sa.Integer(), nullable=False),
        sa.Column("job_type", sa.String(length=32), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("progress", sa.Integer(), nullable=False),
        sa.Column("attempt", sa.Integer(), nullable=False),
        sa.Column("max_attempts", sa.Integer(), nullable=False),
        sa.Column("payload", sa.JSON(), nullable=False),
        sa.Column("result", sa.JSON(), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("available_at", sa.DateTime(), nullable=False),
        sa.Column("locked_by", sa.String(length=128), nullable=True),
        sa.Column("locked_at", sa.DateTime(), nullable=True),
        sa.Column("heartbeat_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("started_at", sa.DateTime(), nullable=True),
        sa.Column("completed_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["meeting_id"], ["meetings.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_processing_jobs_meeting_id", "processing_jobs", ["meeting_id"])
    op.create_index(
        "ix_processing_jobs_status_available",
        "processing_jobs",
        ["status", "available_at", "created_at"],
    )
    op.create_index(
        "uq_processing_jobs_active_meeting_type",
        "processing_jobs",
        ["meeting_id", "job_type"],
        unique=True,
        sqlite_where=sa.text("status IN ('PENDING', 'RUNNING', 'RETRYING')"),
        postgresql_where=sa.text("status IN ('PENDING', 'RUNNING', 'RETRYING')"),
    )


def downgrade() -> None:
    op.drop_index("uq_processing_jobs_active_meeting_type", table_name="processing_jobs")
    op.drop_index("ix_processing_jobs_status_available", table_name="processing_jobs")
    op.drop_index("ix_processing_jobs_meeting_id", table_name="processing_jobs")
    op.drop_table("processing_jobs")
