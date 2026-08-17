"""add speaker segments

Revision ID: 0006_speaker_segments
Revises: 0005_transcription_segments
"""

from alembic import op
import sqlalchemy as sa

revision = "0006_speaker_segments"
down_revision = "0005_transcription_segments"
branch_labels = None
depends_on = None


def upgrade() -> None:
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
    op.create_index(op.f("ix_speaker_segments_id"), "speaker_segments", ["id"], unique=False)
    op.create_index(
        "ix_speaker_segments_transcription_start",
        "speaker_segments",
        ["transcription_id", "start_time"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_speaker_segments_transcription_start", table_name="speaker_segments")
    op.drop_index(op.f("ix_speaker_segments_id"), table_name="speaker_segments")
    op.drop_table("speaker_segments")
