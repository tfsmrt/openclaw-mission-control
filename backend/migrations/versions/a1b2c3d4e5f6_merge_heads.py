"""merge migration heads

Revision ID: a1b2c3d4e5f6
Revises: e3a1b2c4d5f6, f1b2c3d4e5a6
Create Date: 2026-02-28 04:20:00.000000

"""
from __future__ import annotations

from alembic import op


revision = "a1b2c3d4e5f6"
down_revision = ("e3a1b2c4d5f6", "f1b2c3d4e5a6")
branch_labels = None
depends_on = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
