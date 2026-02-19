"""
Zia AI — Action Engine
Central orchestrator: intent parsing → schema lookup → confirmation check →
state machine transition → worker dispatch.
"""

import logging
import time
from typing import Any, Dict, Optional

import redis.asyncio as aioredis

from app.config import settings
from app.core.action_registry import get_action_schema, ACTION_REGISTRY
from app.core.confirmation import ConfirmationEngine
from app.core.state_machine import ActionStateMachine, ConfirmationState
from app.schemas.action import (
    ActionExecution,
    ActionRequest,
    ActionResponse,
    ActionStatus,
    RiskLevel,
)

logger = logging.getLogger("zia.engine")


class ActionThrottled(Exception):
    """Raised when action rate/cooldown limits are exceeded."""
    pass


class ActionEngine:
    """Orchestrates the full action lifecycle."""

    def __init__(self):
        self.confirm_engine = ConfirmationEngine()
        self._redis: Optional[aioredis.Redis] = None

    async def get_redis(self) -> aioredis.Redis:
        if self._redis is None:
            self._redis = aioredis.from_url(settings.REDIS_URL, decode_responses=True)
        return self._redis

    # ── Rate Limiting (Action-Level) ────────────────────

    async def check_action_rate_limit(self, user_id: str, schema) -> None:
        """Enforce per-action cooldown + daily execution cap."""
        redis = await self.get_redis()
        now = time.time()

        # 1. Cooldown
        if schema.cooldown_seconds > 0:
            cooldown_key = f"cd:{user_id}:{schema.action_type}"
            last = await redis.get(cooldown_key)
            if last and (now - float(last)) < schema.cooldown_seconds:
                remaining = schema.cooldown_seconds - (now - float(last))
                raise ActionThrottled(
                    f"Cooldown active. Retry in {remaining:.0f}s"
                )
            await redis.set(cooldown_key, str(now), ex=schema.cooldown_seconds)

        # 2. Daily cap
        if schema.max_daily_executions > 0:
            day_key = f"daily:{user_id}:{schema.action_type}:{time.strftime('%Y%m%d')}"
            count = await redis.incr(day_key)
            if count == 1:
                await redis.expire(day_key, 86400)
            if count > schema.max_daily_executions:
                raise ActionThrottled(
                    f"Daily limit ({schema.max_daily_executions}) reached "
                    f"for {schema.display_name}"
                )

    # ── Action Processing ──────────────────────────────

    async def process_action(
        self,
        request: ActionRequest,
        user: dict,
    ) -> ActionResponse:
        """
        Main entry point: process an action request through the full pipeline.
        """
        # 1. Resolve action type
        action_type = request.action_type
        if not action_type and request.input_text:
            action_type = self._parse_intent(request.input_text)

        if not action_type:
            return ActionResponse(
                execution_id="",
                status=ActionStatus.FAILED,
                message="Could not determine action type from input.",
            )

        schema = get_action_schema(action_type)
        if not schema:
            return ActionResponse(
                execution_id="",
                status=ActionStatus.FAILED,
                message=f"Unknown action type: {action_type}",
            )

        # 2. RBAC check
        user_role = user.get("role", "user")
        if user_role not in schema.allowed_roles:
            return ActionResponse(
                execution_id="",
                status=ActionStatus.REJECTED,
                message=f"Insufficient permissions for {schema.display_name}",
            )

        # 3. Rate limit check
        try:
            await self.check_action_rate_limit(user.get("id", ""), schema)
        except ActionThrottled as e:
            return ActionResponse(
                execution_id="",
                status=ActionStatus.REJECTED,
                message=str(e),
            )

        # 4. Create execution record + state machine
        execution = ActionExecution(
            action_type=action_type,
            params=request.params or {},
            risk_level=schema.risk_level,
            user_id=user.get("id", ""),
            source=request.source,
        )
        sm = ActionStateMachine()

        # 5. Evaluate confirmation rules
        sm.transition(ConfirmationState.RULES_EVAL, "evaluating rules")
        needs_confirm, reasons = self.confirm_engine.evaluate(
            schema, execution.params, user
        )

        if needs_confirm:
            sm.transition(ConfirmationState.PENDING, "confirmation required")
            raw_token, token_hash = self.confirm_engine.generate_token()
            execution.confirmation_token_hash = token_hash
            execution.status = ActionStatus.PENDING

            return ActionResponse(
                execution_id=execution.execution_id,
                status=ActionStatus.PENDING,
                message="Confirmation required",
                confirmation_required=True,
                confirmation_token=raw_token,
                action_preview={
                    "action": schema.display_name,
                    "description": schema.description,
                    "risk_level": schema.risk_level.value,
                    "params": execution.params,
                    "reasons": reasons,
                    "expires_in_seconds": settings.MAX_CONFIRMATION_TTL_MINUTES * 60,
                },
            )

        # 6. Auto-approved → queue for execution
        sm.transition(ConfirmationState.AUTO_APPROVED, "no rules triggered")
        sm.transition(ConfirmationState.QUEUED, "dispatching to worker")
        execution.status = ActionStatus.QUEUED

        return ActionResponse(
            execution_id=execution.execution_id,
            status=ActionStatus.QUEUED,
            message=f"{schema.display_name} queued for execution",
        )

    # ── Intent Parsing (basic keyword matching) ────────

    def _parse_intent(self, text: str) -> Optional[str]:
        """Simple keyword-based intent parser. Replace with NLU in production."""
        text_lower = text.lower()

        intent_map = {
            "gmail.send_email": ["send email", "email", "mail", "write to"],
            "gmail.read_inbox": ["read email", "check mail", "inbox"],
            "twilio.make_call": ["call", "dial", "phone"],
            "twilio.send_whatsapp": ["whatsapp", "message"],
            "filesystem.read_file": ["read file", "open file", "show file"],
            "filesystem.search": ["search file", "find file", "locate"],
            "browser.youtube_play": ["youtube", "play video", "play music"],
            "browser.open_url": ["open url", "browse", "open website"],
            "system.run_command": ["run command", "execute command", "terminal"],
            "macro.work_mode": ["work mode", "start working"],
        }

        for action_type, keywords in intent_map.items():
            if any(kw in text_lower for kw in keywords):
                return action_type

        return None

    @staticmethod
    def get_queue_for_risk(risk_level: RiskLevel) -> str:
        """Map risk level to ARQ queue name."""
        if risk_level == RiskLevel.CRITICAL:
            return "zia:tasks:high"
        elif risk_level in (RiskLevel.HIGH, RiskLevel.MEDIUM):
            return "zia:tasks:default"
        return "zia:tasks:low"
