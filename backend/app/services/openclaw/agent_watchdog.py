"""Agent watchdog — auto-recovers agents stuck in transient states.

Runs as a background task inside the FastAPI lifespan.

Stuck states detected and recovered:
  • "updating"      — stuck > STUCK_UPDATING_AFTER  → reset to "online" + wake
  • "provisioning"  — stuck > STUCK_PROVISION_AFTER → reset to "offline" (needs manual re-provision)

The watchdog only resets agents whose `updated_at` (or `last_seen_at`) has not
changed for longer than the relevant threshold, so in-flight updates are left alone.
"""

from __future__ import annotations

import asyncio
from datetime import timedelta

from sqlalchemy import select, update

from app.core.logging import get_logger
from app.core.time import utcnow
from app.db.session import async_session_maker
from app.models.agents import Agent
from app.models.gateways import Gateway
from app.services.openclaw.gateway_rpc import GatewayConfig, send_message

logger = get_logger(__name__)

# How long an agent can stay in "updating" before we consider it stuck
STUCK_UPDATING_AFTER = timedelta(minutes=5)

# How long an agent can stay in "provisioning" before we give up and mark offline
STUCK_PROVISIONING_AFTER = timedelta(minutes=15)

# How often the watchdog polls (seconds)
WATCHDOG_INTERVAL_SECONDS = 60


async def _recover_stuck_updating(now: any) -> int:
    """Reset agents stuck in 'updating' → 'online' and send a wake message."""
    cutoff = now - STUCK_UPDATING_AFTER
    recovered = 0

    async with async_session_maker() as db:
        result = await db.execute(
            select(Agent).where(
                Agent.status == "updating",
                Agent.updated_at < cutoff,
            )
        )
        stuck_agents = result.scalars().all()

        for agent in stuck_agents:
            logger.warning(
                "watchdog.stuck_updating.recovering",
                extra={
                    "agent_id": str(agent.id),
                    "agent_name": agent.name,
                    "stuck_since": str(agent.updated_at),
                },
            )
            # Reset state
            agent.status = "online"
            agent.provision_action = None
            agent.last_provision_error = "Auto-recovered by watchdog (stuck in updating)"
            agent.updated_at = now
            db.add(agent)

        await db.commit()

        # Send wake messages outside the commit so failures don't roll back the reset
        for agent in stuck_agents:
            if not agent.openclaw_session_id or not agent.gateway_id:
                continue
            try:
                async with async_session_maker() as gw_db:
                    gw_result = await gw_db.execute(
                        select(Gateway).where(Gateway.id == agent.gateway_id)
                    )
                    gateway = gw_result.scalar_one_or_none()
                    if gateway is None:
                        continue
                    config = GatewayConfig(url=gateway.url, token=gateway.token)
                    await send_message(
                        "Resume your current task. Check your assigned tasks on the board and continue working.",
                        session_key=agent.openclaw_session_id,
                        config=config,
                    )
                    logger.info(
                        "watchdog.stuck_updating.wake_sent",
                        extra={"agent_id": str(agent.id), "agent_name": agent.name},
                    )
            except Exception as exc:  # noqa: BLE001
                logger.warning(
                    "watchdog.stuck_updating.wake_failed",
                    extra={"agent_id": str(agent.id), "error": str(exc)},
                )
            recovered += 1

    return recovered


async def _recover_stuck_provisioning(now: any) -> int:
    """Mark agents stuck in 'provisioning' as offline so they can be retried."""
    cutoff = now - STUCK_PROVISIONING_AFTER
    recovered = 0

    async with async_session_maker() as db:
        result = await db.execute(
            select(Agent).where(
                Agent.status == "provisioning",
                Agent.updated_at < cutoff,
            )
        )
        stuck_agents = result.scalars().all()

        for agent in stuck_agents:
            logger.warning(
                "watchdog.stuck_provisioning.marking_offline",
                extra={
                    "agent_id": str(agent.id),
                    "agent_name": agent.name,
                    "stuck_since": str(agent.updated_at),
                },
            )
            agent.status = "offline"
            agent.provision_action = None
            agent.last_provision_error = "Auto-marked offline by watchdog (stuck in provisioning)"
            agent.updated_at = now
            db.add(agent)
            recovered += 1

        await db.commit()

    return recovered


async def run_watchdog_once() -> None:
    """Run one watchdog sweep. Safe to call manually for testing."""
    now = utcnow()
    try:
        updating_recovered = await _recover_stuck_updating(now)
        provisioning_recovered = await _recover_stuck_provisioning(now)
        if updating_recovered or provisioning_recovered:
            logger.info(
                "watchdog.sweep.recovered",
                extra={
                    "updating_recovered": updating_recovered,
                    "provisioning_recovered": provisioning_recovered,
                },
            )
        else:
            logger.debug("watchdog.sweep.nothing_to_recover")
    except Exception as exc:  # noqa: BLE001
        logger.exception("watchdog.sweep.error", extra={"error": str(exc)})


async def watchdog_loop() -> None:
    """Background loop — runs forever inside the FastAPI lifespan."""
    logger.info(
        "watchdog.started",
        extra={
            "interval_seconds": WATCHDOG_INTERVAL_SECONDS,
            "stuck_updating_after_minutes": STUCK_UPDATING_AFTER.total_seconds() / 60,
            "stuck_provisioning_after_minutes": STUCK_PROVISIONING_AFTER.total_seconds() / 60,
        },
    )
    while True:
        await asyncio.sleep(WATCHDOG_INTERVAL_SECONDS)
        await run_watchdog_once()
