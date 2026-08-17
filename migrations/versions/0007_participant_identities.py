"""add participant identities for diarization labels

Revision ID: 0007_participant_identities
Revises: 0006_speaker_segments
"""

import sqlalchemy as sa
from alembic import op

revision = "0007_participant_identities"
down_revision = "0006_speaker_segments"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "participants",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("meeting_id", sa.Integer(), nullable=False),
        sa.Column("speaker_label", sa.String(length=50), nullable=False),
        sa.Column("display_name", sa.String(length=255), nullable=True),
        sa.Column("confirmed", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["meeting_id"], ["meetings.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "meeting_id",
            "speaker_label",
            name="uq_participants_meeting_speaker_label",
        ),
    )
    op.create_index("ix_participants_id", "participants", ["id"], unique=False)
    op.create_index("ix_participants_meeting_id", "participants", ["meeting_id"], unique=False)

    op.execute(
        sa.text(
            """
            INSERT INTO participants (
                meeting_id, speaker_label, display_name, confirmed, created_at, updated_at
            )
            SELECT DISTINCT
                a.meeting_id,
                ss.speaker_label,
                NULL,
                0,
                CURRENT_TIMESTAMP,
                CURRENT_TIMESTAMP
            FROM speaker_segments AS ss
            JOIN transcriptions AS t ON t.id = ss.transcription_id
            JOIN audios AS a ON a.id = t.audio_id
            WHERE a.deleted_at IS NULL
              AND ss.speaker_label IS NOT NULL
              AND ss.speaker_label <> ''
            """
        )
    )


def downgrade() -> None:
    op.drop_index("ix_participants_meeting_id", table_name="participants")
    op.drop_index("ix_participants_id", table_name="participants")
    op.drop_table("participants")
