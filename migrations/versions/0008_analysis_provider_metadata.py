"""add analysis provider metadata

Revision ID: 0008_analysis_provider_metadata
Revises: 0007_participant_identities
"""

from alembic import op
import sqlalchemy as sa

revision = "0008_analysis_provider_metadata"
down_revision = "0007_participant_identities"
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table("meeting_analysis") as batch_op:
        batch_op.add_column(sa.Column("provider", sa.String(length=50), nullable=True))
        batch_op.add_column(sa.Column("model_name", sa.String(length=100), nullable=True))


def downgrade() -> None:
    with op.batch_alter_table("meeting_analysis") as batch_op:
        batch_op.drop_column("model_name")
        batch_op.drop_column("provider")
