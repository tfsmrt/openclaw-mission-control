"""Auto-archive tasks that have been in 'done' status for more than 3 days.

Runs as a background task inside the FastAPI lifespan, checking once per hour.
"""

from __future__ import annotations

import asyncio
import logging
from datetime import timedelta

from sqlalchemy import update
from sqlmodel import col

from app.core.time import utcnow
from app.db.session import async_session_maker
from app.models.tasks import Task

logger = logging.getLogger(__name__)

ARCHIVE_AFTER = timedelta(days=3)
CHECK_INTERVAL_SECONDS = 3600  # 1 hour


async def _archive_done_tasks() -> int:
    """Move done tasks older than ARCHIVE_AFTER to archived status."""
    cutoff = utcnow() - ARCHIVE_AFTER
    async with async_session_maker() as session:
        result = await session.exec(
            update(Task)
            .where(
                col(Task.status) == "done",
                col(Task.updated_at) < cutoff,
            )
            .values(status="archived", updated_at=utcnow())
        )
        await session.commit()
        return result.rowcount  # type: ignore[union-attr]


async def auto_archive_loop() -> None:
    """Periodically archive stale done tasks."""
    while True:
        try:
            count = await _archive_done_tasks()
            if count > 0:
                logger.info("task.auto_archive archived=%d", count)
        except asyncio.CancelledError:
            raise
        except Exception:
            logger.exception("task.auto_archive.error")
        await asyncio.sleep(CHECK_INTERVAL_SECONDS)
