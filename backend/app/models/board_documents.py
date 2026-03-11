"""Board documents model for storing docs/guides as board context."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID, uuid4

from sqlmodel import Field, SQLModel


class BoardDocument(SQLModel, table=True):
    """Document/guide attached to a board for agent context."""

    __tablename__ = "board_documents"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    board_id: UUID = Field(foreign_key="boards.id", index=True)
    title: str = Field(index=True)
    content: str  # Markdown content
    description: str | None = None  # Brief summary
    order: int = Field(default=0, index=True)  # Sort order
    created_by_user_id: UUID | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.utcnow())
    updated_at: datetime = Field(default_factory=lambda: datetime.utcnow())


class BoardDocumentRead(SQLModel):
    """Board document payload returned from read endpoints."""

    id: UUID
    board_id: UUID
    title: str
    content: str
    description: str | None = None
    order: int
    created_by_user_id: UUID | None = None
    created_at: datetime
    updated_at: datetime


class BoardDocumentCreate(SQLModel):
    """Payload for creating a board document."""

    title: str
    content: str
    description: str | None = None
    order: int = 0


class BoardDocumentUpdate(SQLModel):
    """Payload for updating a board document."""

    title: str | None = None
    content: str | None = None
    description: str | None = None
    order: int | None = None
