"""Add timestamped transcription segments and one transcription per audio.

Revision ID: 0005_transcription_segments
Revises: 0004_processing_jobs
Create Date: 2026-08-16
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0005_transcription_segments"
down_revision: Union[str, None] = "0004_processing_jobs"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    duplicates = op.get_bind().execute(
        sa.text(
            "SELECT audio_id, COUNT(*) AS total FROM transcriptions "
            "GROUP BY audio_id HAVING COUNT(*) > 1 LIMIT 1"
        )
    ).first()
    if duplicates is not None:
        raise RuntimeError(
            "Cannot enforce one transcription per audio: duplicate transcriptions exist"
        )

    op.create_index(
        "uq_transcriptions_audio_id",
        "transcriptions",
        ["audio_id"],
        unique=True,
    )
    op.create_table(
        "transcription_segments",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("transcription_id", sa.Integer(), nullable=False),
        sa.Column("sequence", sa.Integer(), nullable=False),
        sa.Column("start_time", sa.Float(), nullable=False),
        sa.Column("end_time", sa.Float(), nullable=False),
        sa.Column("text", sa.Text(), nullable=False),
        sa.Column("confidence", sa.Float(), nullable=True),
        sa.ForeignKeyConstraint(
            ["transcription_id"],
            ["transcriptions.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "transcription_id",
            "sequence",
            name="uq_transcription_segment_sequence",
        ),
    )
    op.create_index(
        "ix_transcription_segments_transcription_id",
        "transcription_segments",
        ["transcription_id"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_transcription_segments_transcription_id",
        table_name="transcription_segments",
    )
    op.drop_table("transcription_segments")
    op.drop_index("uq_transcriptions_audio_id", table_name="transcriptions")
