"""index speaker segments for diarization reads

Revision ID: 0006_speaker_segments
Revises: 0005_transcription_segments
"""

from alembic import op

revision = "0006_speaker_segments"
down_revision = "0005_transcription_segments"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_index(
        "ix_speaker_segments_transcription_start",
        "speaker_segments",
        ["transcription_id", "start_time"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_speaker_segments_transcription_start", table_name="speaker_segments")
