"""Add technical audio metadata columns.

Revision ID: 0002_audio_media_metadata
Revises: 0001_initial_schema
Create Date: 2026-08-16
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0002_audio_media_metadata"
down_revision: Union[str, None] = "0001_initial_schema"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Persist metadata extracted by ffprobe for uploaded audio."""
    with op.batch_alter_table("audios") as batch_op:
        batch_op.add_column(sa.Column("codec_name", sa.String(length=64), nullable=True))
        batch_op.add_column(sa.Column("channels", sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column("sample_rate", sa.Integer(), nullable=True))


def downgrade() -> None:
    """Remove ffprobe metadata fields."""
    with op.batch_alter_table("audios") as batch_op:
        batch_op.drop_column("sample_rate")
        batch_op.drop_column("channels")
        batch_op.drop_column("codec_name")
