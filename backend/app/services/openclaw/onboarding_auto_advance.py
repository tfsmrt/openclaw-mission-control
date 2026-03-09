"""Self-contained onboarding auto-advancer.

When a user posts an answer the backend calls ``auto_advance`` which
immediately posts the next question (or the completion payload) using
the gateway-agent token — no live gateway-agent session required.
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any

from sqlmodel.ext.asyncio.session import AsyncSession

from app.models.board_onboarding import BoardOnboardingSession
from app.models.boards import Board

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Question definitions — order matters
# ---------------------------------------------------------------------------

_QUESTIONS: list[dict[str, Any]] = [
    {
        "key": "goal",
        "question": "What is the primary goal for this board — what should the lead agent focus on?",
        "options": [
            {"id": "1", "label": "Analyse and report on user, order, and product data"},
            {"id": "2", "label": "Monitor and summarise key business metrics (revenue, signups, churn)"},
            {"id": "3", "label": "Investigate specific data on demand (ad-hoc queries and lookups)"},
            {"id": "4", "label": "Other (I'll type it)"},
        ],
    },
    {
        "key": "data_priority",
        "question": "Which data area should the lead agent prioritise first?",
        "options": [
            {"id": "1", "label": "Orders & revenue (sales performance, paid vs free)"},
            {"id": "2", "label": "Users & signups (growth, country breakdown, personas)"},
            {"id": "3", "label": "Products & downloads (catalogue performance, reviews)"},
            {"id": "4", "label": "All equally — rotate through them"},
        ],
    },
    {
        "key": "report_format",
        "question": "How should the lead agent deliver findings and reports?",
        "options": [
            {"id": "1", "label": "Bullet-point summaries — quick, scannable"},
            {"id": "2", "label": "Narrative paragraphs — context and interpretation included"},
            {"id": "3", "label": "Mixed — bullets for data, prose for insights"},
            {"id": "4", "label": "Raw data tables — I will interpret myself"},
        ],
    },
    {
        "key": "autonomy",
        "question": "How autonomous should the lead agent be?",
        "options": [
            {"id": "1", "label": "Ask first — confirm with me before taking action"},
            {"id": "2", "label": "Balanced — act independently, flag blockers"},
            {"id": "3", "label": "Autonomous — run fully on its own, update me on results"},
        ],
    },
    {
        "key": "cadence",
        "question": "How often should the lead agent send you updates?",
        "options": [
            {"id": "1", "label": "As soon as something notable happens"},
            {"id": "2", "label": "Hourly digest"},
            {"id": "3", "label": "Daily summary"},
            {"id": "4", "label": "Weekly report"},
        ],
    },
    {
        "key": "agent_name",
        "question": "Choose a first-name for the lead agent (type your own or pick one).",
        "options": [
            {"id": "1", "label": "Rex"},
            {"id": "2", "label": "Nova"},
            {"id": "3", "label": "Iris"},
            {"id": "4", "label": "Atlas"},
            {"id": "5", "label": "Other (I'll type it)"},
        ],
    },
    {
        "key": "extra",
        "question": "Anything else the lead agent should know? (constraints, tools, priorities)",
        "options": [
            {"id": "1", "label": "No, that's everything"},
            {"id": "2", "label": "Yes (I'll type it)"},
        ],
    },
]

# ---------------------------------------------------------------------------
# Value mappers
# ---------------------------------------------------------------------------

_AUTONOMY_MAP = {
    "ask first": "ask_first",
    "balanced": "balanced",
    "autonomous": "autonomous",
}
_CADENCE_MAP = {
    "as soon as": "asap",
    "hourly": "hourly",
    "daily": "daily",
    "weekly": "weekly",
}
_FORMAT_MAP = {
    "bullet": "bullets",
    "narrative": "narrative",
    "mixed": "mixed",
    "raw": "bullets",
}


def _map(text: str, mapping: dict[str, str], default: str) -> str:
    tl = text.lower()
    for k, v in mapping.items():
        if k in tl:
            return v
    return default


def _extract_agent_name(answer: str) -> str:
    """Return the agent name from the answer text."""
    built_in = {"Rex", "Nova", "Iris", "Atlas"}
    for name in built_in:
        if name.lower() in answer.lower():
            return name
    # strip "Other (I'll type it):" prefix if present
    clean = answer.split(":", 1)[-1].strip()
    if clean:
        return clean.split()[0].capitalize()
    return "Rex"


def _build_completion(answers: list[str], board_name: str) -> dict[str, Any]:
    """Construct the BoardOnboardingAgentComplete payload from collected answers."""
    goal_ans = answers[0] if len(answers) > 0 else ""
    priority_ans = answers[1] if len(answers) > 1 else ""
    format_ans = answers[2] if len(answers) > 2 else ""
    autonomy_ans = answers[3] if len(answers) > 3 else ""
    cadence_ans = answers[4] if len(answers) > 4 else ""
    name_ans = answers[5] if len(answers) > 5 else "Rex"
    extra_ans = answers[6] if len(answers) > 6 else ""

    agent_name = _extract_agent_name(name_ans)
    autonomy = _map(autonomy_ans, _AUTONOMY_MAP, "balanced")
    cadence = _map(cadence_ans, _CADENCE_MAP, "daily")
    output_fmt = _map(format_ans, _FORMAT_MAP, "mixed")
    verbosity = "balanced"

    # Build objective from goal + priority answers
    objective = (
        f"{board_name}: {goal_ans.rstrip('.')}. "
        f"Priority focus: {priority_ans.rstrip('.')}."
    )

    # Success metrics derived from priority
    if "order" in priority_ans.lower() or "revenue" in priority_ans.lower():
        metric = "Revenue and order performance tracked weekly"
        target = "Consistent reporting with trend analysis"
    elif "user" in priority_ans.lower() or "signup" in priority_ans.lower():
        metric = "User growth and engagement tracked weekly"
        target = "Consistent reporting with country and persona breakdown"
    else:
        metric = "Key business metrics tracked and reported"
        target = "Consistent coverage across users, orders, and products"

    custom_instructions = extra_ans if extra_ans and "no" not in extra_ans.lower() else ""

    return {
        "status": "complete",
        "board_type": "goal",
        "objective": objective,
        "success_metrics": {"metric": metric, "target": target},
        "user_profile": {
            "pronouns": None,
            "timezone": "Asia/Dhaka",
            "notes": None,
            "context": None,
        },
        "lead_agent": {
            "name": agent_name,
            "identity_profile": {
                "role": "Data Intelligence Lead",
                "communication_style": f"{output_fmt.replace('bullets','direct, bullet-driven').replace('mixed','direct, mixed').replace('narrative','detailed narrative')}, analytical",
                "emoji": "📊",
            },
            "autonomy_level": autonomy,
            "verbosity": verbosity,
            "output_format": output_fmt,
            "update_cadence": cadence,
            "custom_instructions": custom_instructions or None,
        },
    }


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

async def auto_advance(
    *,
    session: AsyncSession,
    board: Board,
    onboarding: BoardOnboardingSession,
) -> None:
    """Post the next onboarding question (or completion) using the gateway-agent token.

    Called immediately after the user's answer is saved.  Uses an internal
    HTTP call so it respects all existing auth/validation logic.
    """
    import httpx
    from app.core.config import settings

    # Collect user answers so far (skip the long initial prompt)
    messages = list(onboarding.messages or [])
    user_answers = [
        m["content"]
        for m in messages
        if m.get("role") == "user"
        and "BOARD ONBOARDING REQUEST" not in m.get("content", "")
        and len(m.get("content", "")) < 2000
    ]

    answer_count = len(user_answers)
    logger.info(
        "onboarding.auto_advance board_id=%s answer_count=%d", board.id, answer_count
    )

    # Resolve gateway-agent token from DB
    from app.models.agents import Agent
    from sqlmodel import select, col

    gw_agent = (
        await session.exec(
            select(Agent).where(
                col(Agent.gateway_id) == board.gateway_id,
                col(Agent.openclaw_session_id).contains("mc-gateway-"),
            )
        )
    ).first()

    if gw_agent is None:
        logger.warning("onboarding.auto_advance.no_gateway_agent board_id=%s", board.id)
        return

    # Verify we have a usable token hash — re-mint if needed
    from app.services.openclaw.db_agent_state import mint_agent_token, verify_agent_token
    from app.core.time import utcnow
    from datetime import timedelta

    # Check if current token works; if not, mint a new one
    token_to_use: str | None = None

    # Always mint a fresh token to avoid stale-token 401s
    raw_token = mint_agent_token(gw_agent)
    gw_agent.checkin_deadline_at = utcnow() + timedelta(hours=2)
    session.add(gw_agent)
    await session.commit()
    token_to_use = raw_token

    base_url = str(settings.base_url).rstrip("/") if hasattr(settings, "base_url") else "https://api.somrat.tech"
    endpoint = f"{base_url}/api/v1/boards/{board.id}/onboarding/agent"

    if answer_count < len(_QUESTIONS):
        q = _QUESTIONS[answer_count]
        payload = {"question": q["question"], "options": q["options"]}
    else:
        payload = _build_completion(user_answers, board.name)

    try:
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.post(
                endpoint,
                json=payload,
                headers={"X-Agent-Token": token_to_use, "Content-Type": "application/json"},
            )
            if resp.status_code == 200:
                logger.info(
                    "onboarding.auto_advance.posted board_id=%s answer_count=%d status=ok",
                    board.id,
                    answer_count,
                )
            else:
                logger.warning(
                    "onboarding.auto_advance.post_failed board_id=%s status=%d body=%s",
                    board.id,
                    resp.status_code,
                    resp.text[:200],
                )
    except Exception as exc:
        logger.error("onboarding.auto_advance.error board_id=%s error=%s", board.id, exc)
