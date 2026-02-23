"""drop preferred_name from users — always use authoritative name from auth provider

Revision ID: d7e8f9a0b1c2
Revises: c1a2b3d4e5f6
Create Date: 2026-02-23 09:32:00.000000

preferred_name was a user-settable nickname that duplicated (and could contradict)
the authoritative name sourced from Clerk. Removing it simplifies attribution and
eliminates the class of bugs where the field was set to another user's name.
"""

from __future__ import annotations

from alembic import op


# revision identifiers, used by Alembic.
revision = "d7e8f9a0b1c2"
down_revision = "c1a2b3d4e5f6"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_column("users", "preferred_name")


def downgrade() -> None:
    import sqlalchemy as sa

    op.add_column(
        "users",
        sa.Column("preferred_name", sa.String(), nullable=True),
    )
