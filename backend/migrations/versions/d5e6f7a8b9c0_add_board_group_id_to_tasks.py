"""Add board_group_id to tasks for group-level task support.

Revision ID: d5e6f7a8b9c0
Revises: c4d5e6f7a8b9
Create Date: 2026-03-08 09:00:00.000000
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "d5e6f7a8b9c0"
down_revision = "c4d5e6f7a8b9"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("tasks", sa.Column("board_group_id", sa.Uuid(), nullable=True))
    op.create_index("ix_tasks_board_group_id", "tasks", ["board_group_id"])
    op.create_foreign_key(
        "fk_tasks_board_group_id_board_groups",
        "tasks",
        "board_groups",
        ["board_group_id"],
        ["id"],
        ondelete="CASCADE",
    )


def downgrade() -> None:
    op.drop_constraint(
        "fk_tasks_board_group_id_board_groups", "tasks", type_="foreignkey"
    )
    op.drop_index("ix_tasks_board_group_id", table_name="tasks")
    op.drop_column("tasks", "board_group_id")
