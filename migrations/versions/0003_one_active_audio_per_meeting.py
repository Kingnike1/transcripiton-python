"""Enforce one active audio per meeting.

Revision ID: 0003_one_active_audio_per_meeting
Revises: 0002_audio_media_metadata
Create Date: 2026-08-16
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0003_one_active_audio_per_meeting"
down_revision: Union[str, None] = "0002_audio_media_metadata"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Allow only one non-deleted audio row for each meeting."""
    connection = op.get_bind()
    duplicates = connection.execute(
        sa.text(
            """
            SELECT meeting_id, COUNT(*) AS active_count
            FROM audios
            WHERE deleted_at IS NULL
            GROUP BY meeting_id
            HAVING COUNT(*) > 1
            """
        )
    ).fetchall()
    if duplicates:
        meeting_ids = ", ".join(str(row[0]) for row in duplicates)
        raise RuntimeError(
            "Cannot enforce one active audio per meeting; duplicate active audios "
            f"exist for meeting IDs: {meeting_ids}"
        )

    op.create_index(
        "uq_audios_active_meeting",
        "audios",
        ["meeting_id"],
        unique=True,
        sqlite_where=sa.text("deleted_at IS NULL"),
        postgresql_where=sa.text("deleted_at IS NULL"),
    )


def downgrade() -> None:
    """Remove the one-active-audio integrity rule."""
    op.drop_index("uq_audios_active_meeting", table_name="audios")
