"""add board documents table

Revision ID: c1d2e3f4a5b6
Revises: b1c2d3e4f5a6
Create Date: 2026-03-11 07:25:00.000000

Add board documents table for storing docs/guides as board context for agents.
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "c1d2e3f4a5b6"
down_revision = "b1c2d3e4f5a6"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create board_documents table
    op.create_table(
        "board_documents",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("board_id", sa.Uuid(), nullable=False),
        sa.Column("title", sa.String(), nullable=False),
        sa.Column("content", sa.String(), nullable=False),
        sa.Column("description", sa.String(), nullable=True),
        sa.Column("order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_by_user_id", sa.Uuid(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["board_id"], ["boards.id"], name="fk_board_documents_board_id"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_board_documents_board_id"),
        "board_documents",
        ["board_id"],
    )
    op.create_index(
        op.f("ix_board_documents_title"),
        "board_documents",
        ["title"],
    )
    op.create_index(
        op.f("ix_board_documents_order"),
        "board_documents",
        ["order"],
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_board_documents_order"), table_name="board_documents")
    op.drop_index(op.f("ix_board_documents_title"), table_name="board_documents")
    op.drop_index(op.f("ix_board_documents_board_id"), table_name="board_documents")
    op.drop_table("board_documents")
