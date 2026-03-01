"""Add board_secrets table.

Revision ID: b1a2c3d4e5f7
Revises: a1b2c3d4e5f6
Create Date: 2026-03-01 08:00:00.000000
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "b1a2c3d4e5f7"
down_revision = "a1b2c3d4e5f6"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "board_secrets",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("organization_id", sa.Uuid(), nullable=False),
        sa.Column("board_id", sa.Uuid(), nullable=False),
        sa.Column("key", sa.String(), nullable=False),
        sa.Column("encrypted_value", sa.Text(), nullable=False),
        sa.Column("description", sa.String(), nullable=False, server_default=""),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["board_id"], ["boards.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_board_secrets_board_id", "board_secrets", ["board_id"])
    op.create_index("ix_board_secrets_organization_id", "board_secrets", ["organization_id"])
    op.create_index("ix_board_secrets_key", "board_secrets", ["key"])
    op.create_unique_constraint("uq_board_secrets_board_key", "board_secrets", ["board_id", "key"])


def downgrade() -> None:
    op.drop_table("board_secrets")
