"""Board secrets model — encrypted per-board key/value credentials."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID, uuid4

from sqlmodel import Field

from app.core.time import utcnow
from app.models.tenancy import TenantScoped


class BoardSecret(TenantScoped, table=True):
    """Encrypted credential/secret scoped to a board, injected into agent workspaces."""

    __tablename__ = "board_secrets"  # pyright: ignore[reportAssignmentType]

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    organization_id: UUID = Field(foreign_key="organizations.id", index=True)
    board_id: UUID = Field(foreign_key="boards.id", index=True)
    key: str = Field(index=True)
    encrypted_value: str  # Fernet-encrypted
    description: str = Field(default="")
    created_at: datetime = Field(default_factory=utcnow)
    updated_at: datetime = Field(default_factory=utcnow)
