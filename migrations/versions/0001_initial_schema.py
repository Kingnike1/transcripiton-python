"""Initial AMIP schema baseline.

Revision ID: 0001_initial_schema
Revises: None
Create Date: 2026-08-16
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0001_initial_schema"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create the schema represented by the current SQLAlchemy models."""
    op.create_table(
        "meetings",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_meetings_id"), "meetings", ["id"], unique=False)

    op.create_table(
        "audios",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("meeting_id", sa.Integer(), nullable=False),
        sa.Column("filename", sa.String(length=255), nullable=False),
        sa.Column("file_path", sa.String(length=512), nullable=False),
        sa.Column("duration", sa.Integer(), nullable=True),
        sa.Column("file_size", sa.Integer(), nullable=True),
        sa.Column("mime_type", sa.String(length=50), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["meeting_id"], ["meetings.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_audios_id"), "audios", ["id"], unique=False)

    op.create_table(
        "meeting_analysis",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("meeting_id", sa.Integer(), nullable=False),
        sa.Column("summary", sa.Text(), nullable=True),
        sa.Column("action_items", sa.Text(), nullable=True),
        sa.Column("decisions", sa.Text(), nullable=True),
        sa.Column("risks", sa.Text(), nullable=True),
        sa.Column("open_questions", sa.Text(), nullable=True),
        sa.Column("follow_up_tasks", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["meeting_id"], ["meetings.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("meeting_id"),
    )
    op.create_index(
        op.f("ix_meeting_analysis_id"), "meeting_analysis", ["id"], unique=False
    )

    op.create_table(
        "transcriptions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("audio_id", sa.Integer(), nullable=False),
        sa.Column("text", sa.Text(), nullable=False),
        sa.Column("language", sa.String(length=10), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["audio_id"], ["audios.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_transcriptions_id"), "transcriptions", ["id"], unique=False
    )

    op.create_table(
        "speaker_segments",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("transcription_id", sa.Integer(), nullable=False),
        sa.Column("speaker_label", sa.String(length=50), nullable=True),
        sa.Column("start_time", sa.Float(), nullable=False),
        sa.Column("end_time", sa.Float(), nullable=False),
        sa.Column("text", sa.Text(), nullable=False),
        sa.Column("confidence", sa.Float(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["transcription_id"], ["transcriptions.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_speaker_segments_id"), "speaker_segments", ["id"], unique=False
    )


def downgrade() -> None:
    """Remove the complete baseline schema in dependency-safe order."""
    op.drop_index(op.f("ix_speaker_segments_id"), table_name="speaker_segments")
    op.drop_table("speaker_segments")
    op.drop_index(op.f("ix_transcriptions_id"), table_name="transcriptions")
    op.drop_table("transcriptions")
    op.drop_index(op.f("ix_meeting_analysis_id"), table_name="meeting_analysis")
    op.drop_table("meeting_analysis")
    op.drop_index(op.f("ix_audios_id"), table_name="audios")
    op.drop_table("audios")
    op.drop_index(op.f("ix_meetings_id"), table_name="meetings")
    op.drop_table("meetings")
