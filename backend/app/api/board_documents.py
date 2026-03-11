"""API endpoints for board documents/guides."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, status
from fastapi_pagination.limit_offset import LimitOffsetPage
from sqlmodel import col, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import SESSION_DEP
from app.models.board_documents import (
    BoardDocument,
    BoardDocumentCreate,
    BoardDocumentRead,
    BoardDocumentUpdate,
)
from app.db import crud
from app.db.pagination import paginate
from app.schemas.pagination import DefaultLimitOffsetPage

router = APIRouter(prefix="/boards/{board_id}/documents", tags=["board-documents"])


@router.get("", response_model=DefaultLimitOffsetPage[BoardDocumentRead])
async def list_board_documents(
    board_id: UUID,
    session: AsyncSession = SESSION_DEP,
) -> LimitOffsetPage[BoardDocumentRead]:
    """List all documents for a board."""
    statement = (
        select(BoardDocument)
        .where(col(BoardDocument.board_id) == board_id)
        .order_by(col(BoardDocument.order), col(BoardDocument.created_at))
    )
    return await paginate(session, statement)


@router.post("", response_model=BoardDocumentRead, status_code=status.HTTP_201_CREATED)
async def create_board_document(
    board_id: UUID,
    payload: BoardDocumentCreate,
    session: AsyncSession = SESSION_DEP,
) -> BoardDocumentRead:
    """Create a new document for a board."""
    doc = BoardDocument(
        board_id=board_id,
        title=payload.title,
        content=payload.content,
        description=payload.description,
        order=payload.order,
    )
    session.add(doc)
    await session.commit()
    await session.refresh(doc)
    return BoardDocumentRead.model_validate(doc, from_attributes=True)


@router.get("/{doc_id}", response_model=BoardDocumentRead)
async def get_board_document(
    board_id: UUID,
    doc_id: UUID,
    session: AsyncSession = SESSION_DEP,
) -> BoardDocumentRead:
    """Get a specific board document."""
    doc = await session.exec(
        select(BoardDocument).where(
            col(BoardDocument.id) == doc_id,
            col(BoardDocument.board_id) == board_id,
        )
    )
    doc = doc.first()
    if doc is None:
        from fastapi import HTTPException
        raise HTTPException(status_code=404)
    return BoardDocumentRead.model_validate(doc, from_attributes=True)


@router.patch("/{doc_id}", response_model=BoardDocumentRead)
async def update_board_document(
    board_id: UUID,
    doc_id: UUID,
    payload: BoardDocumentUpdate,
    session: AsyncSession = SESSION_DEP,
) -> BoardDocumentRead:
    """Update a board document."""
    doc = await session.exec(
        select(BoardDocument).where(
            col(BoardDocument.id) == doc_id,
            col(BoardDocument.board_id) == board_id,
        )
    )
    doc = doc.first()
    if doc is None:
        from fastapi import HTTPException
        raise HTTPException(status_code=404)
    
    if payload.title is not None:
        doc.title = payload.title
    if payload.content is not None:
        doc.content = payload.content
    if payload.description is not None:
        doc.description = payload.description
    if payload.order is not None:
        doc.order = payload.order
    
    session.add(doc)
    await session.commit()
    await session.refresh(doc)
    return BoardDocumentRead.model_validate(doc, from_attributes=True)


@router.delete("/{doc_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_board_document(
    board_id: UUID,
    doc_id: UUID,
    session: AsyncSession = SESSION_DEP,
) -> None:
    """Delete a board document."""
    await crud.delete_where(
        session,
        BoardDocument,
        col(BoardDocument.id) == doc_id,
        col(BoardDocument.board_id) == board_id,
        commit=True,
    )
