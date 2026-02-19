"""
Zia AI — Audit Service
Structured audit logging to PostgreSQL with sensitive-field redaction.
"""

import logging
from datetime import datetime
from typing import Any, Dict, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.action_log import ActionLog

logger = logging.getLogger("zia.audit")

# Fields to redact in audit logs
SENSITIVE_FIELDS = {"password", "body", "content", "access_token", "refresh_token", "secret"}


def redact_params(params: Dict[str, Any]) -> Dict[str, Any]:
    """Redact sensitive fields from params before logging."""
    redacted = {}
    for key, val in params.items():
        if key.lower() in SENSITIVE_FIELDS:
            redacted[key] = "***REDACTED***"
        elif isinstance(val, dict):
            redacted[key] = redact_params(val)
        else:
            redacted[key] = val
    return redacted


class AuditService:
    """Database-backed audit logging."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def log_action(
        self,
        user_id: str,
        execution_id: str,
        action_type: str,
        params: Dict[str, Any],
        risk_level: str,
        status: str,
        source: str = "text",
        result: Optional[Dict] = None,
        error: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        duration_ms: Optional[int] = None,
        state_history: list = None,
    ) -> ActionLog:
        """Log an action execution to the audit trail."""
        log = ActionLog(
            user_id=user_id,
            execution_id=execution_id,
            action_type=action_type,
            params=redact_params(params),
            risk_level=risk_level,
            status=status,
            source=source,
            result=result,
            error=error,
            ip_address=ip_address,
            user_agent=user_agent,
            duration_ms=duration_ms,
            state_history=state_history or [],
        )

        if status in ("completed", "failed"):
            log.completed_at = datetime.utcnow()

        self.db.add(log)
        await self.db.flush()

        logger.info(
            "audit",
            extra={
                "user_id": user_id,
                "action_type": action_type,
                "status": status,
                "execution_id": execution_id,
            },
        )
        return log
