"""add author fields to activity_events for human comment attribution

Revision ID: c1a2b3d4e5f6
Revises: b497b348ebb4
Create Date: 2026-02-23 07:15:00.000000

"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = 'c1a2b3d4e5f6'
down_revision = 'b497b348ebb4'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add created_by_user_id (FK to users) for audit trail
    op.add_column(
        'activity_events',
        sa.Column('created_by_user_id', postgresql.UUID(as_uuid=True), nullable=True),
    )
    op.create_foreign_key(
        'fk_activity_events_created_by_user_id',
        'activity_events',
        'users',
        ['created_by_user_id'],
        ['id'],
        ondelete='SET NULL',
    )
    op.create_index(
        'ix_activity_events_created_by_user_id',
        'activity_events',
        ['created_by_user_id'],
    )

    # Add denormalized author_name for fast display (no join needed at read time)
    op.add_column(
        'activity_events',
        sa.Column('author_name', sa.String(), nullable=True),
    )


def downgrade() -> None:
    op.drop_index('ix_activity_events_created_by_user_id', table_name='activity_events')
    op.drop_constraint('fk_activity_events_created_by_user_id', 'activity_events', type_='foreignkey')
    op.drop_column('activity_events', 'created_by_user_id')
    op.drop_column('activity_events', 'author_name')
