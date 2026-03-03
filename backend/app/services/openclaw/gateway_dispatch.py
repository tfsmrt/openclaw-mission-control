"""DB-backed gateway config resolution and message dispatch helpers.

This module exists to keep `app.api.*` thin: APIs should call OpenClaw services, not
directly orchestrate gateway RPC calls.
"""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from app.models.boards import Board
from app.models.gateways import Gateway
from app.services.openclaw.constants import OFFLINE_AFTER
from app.services.openclaw.db_service import OpenClawDBService
from app.services.openclaw.gateway_resolver import (
    gateway_client_config,
    get_gateway_for_board,
    optional_gateway_client_config,
    require_gateway_for_board,
)
from app.services.openclaw.gateway_rpc import GatewayConfig as GatewayClientConfig
from app.services.openclaw.gateway_rpc import OpenClawGatewayError, ensure_session, send_message

WAKE_MESSAGE = (
    "Read HEARTBEAT.md if it exists (workspace context). "
    "Follow it strictly. Do not infer or repeat old tasks from prior chats. "
    "If nothing needs attention, reply HEARTBEAT_OK."
)


def _is_agent_offline(last_seen_at: datetime | None) -> bool:
    """Return True if the agent hasn't been seen within OFFLINE_AFTER."""
    if last_seen_at is None:
        return True
    ts = last_seen_at if last_seen_at.tzinfo else last_seen_at.replace(tzinfo=timezone.utc)
    return (datetime.now(timezone.utc) - ts) > OFFLINE_AFTER


class GatewayDispatchService(OpenClawDBService):
    """Resolve gateway config for boards and dispatch messages to agent sessions."""

    async def optional_gateway_config_for_board(
        self,
        board: Board,
    ) -> GatewayClientConfig | None:
        gateway = await get_gateway_for_board(self.session, board)
        return optional_gateway_client_config(gateway)

    async def require_gateway_config_for_board(
        self,
        board: Board,
    ) -> tuple[Gateway, GatewayClientConfig]:
        gateway = await require_gateway_for_board(self.session, board)
        return gateway, gateway_client_config(gateway)

    async def wake_agent_if_offline(
        self,
        *,
        session_key: str,
        config: GatewayClientConfig,
        agent_name: str,
        last_seen_at: datetime | None,
    ) -> None:
        """Send a wake message if the agent appears offline. Silently ignores errors."""
        if not _is_agent_offline(last_seen_at):
            return
        logger = _get_logger()
        logger.info(
            "dispatch.wake_agent",
            extra={"agent_name": agent_name, "session_key": session_key},
        )
        try:
            await ensure_session(session_key, config=config, label=agent_name)
            await send_message(
                WAKE_MESSAGE,
                session_key=session_key,
                config=config,
                deliver=True,
            )
        except OpenClawGatewayError:
            logger.warning(
                "dispatch.wake_agent.failed",
                extra={"agent_name": agent_name, "session_key": session_key},
            )

    async def send_agent_message(
        self,
        *,
        session_key: str,
        config: GatewayClientConfig,
        agent_name: str,
        message: str,
        deliver: bool = False,
        last_seen_at: datetime | None = None,
    ) -> None:
        # Wake offline agents before delivering task notifications.
        if last_seen_at is not None:
            await self.wake_agent_if_offline(
                session_key=session_key,
                config=config,
                agent_name=agent_name,
                last_seen_at=last_seen_at,
            )
        await ensure_session(session_key, config=config, label=agent_name)
        await send_message(message, session_key=session_key, config=config, deliver=deliver)

    async def try_send_agent_message(
        self,
        *,
        session_key: str,
        config: GatewayClientConfig,
        agent_name: str,
        message: str,
        deliver: bool = False,
        last_seen_at: datetime | None = None,
    ) -> OpenClawGatewayError | None:
        try:
            await self.send_agent_message(
                session_key=session_key,
                config=config,
                agent_name=agent_name,
                message=message,
                deliver=deliver,
                last_seen_at=last_seen_at,
            )
        except OpenClawGatewayError as exc:
            return exc
        return None

    @staticmethod
    def resolve_trace_id(correlation_id: str | None, *, prefix: str) -> str:
        normalized = (correlation_id or "").strip()
        if normalized:
            return normalized
        return f"{prefix}:{uuid4().hex[:12]}"


def _get_logger():  # type: ignore[return]
    from app.core.logging import get_logger

    return get_logger(__name__)
