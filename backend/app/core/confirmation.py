"""
Zia AI — Confirmation Rules Engine
Evaluates whether an action needs user confirmation and manages confirmation tokens.
"""

import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Any, Dict, List, Tuple

from app.config import settings
from app.schemas.action import ActionSchema, RiskLevel

CONFIRMATION_TTL = timedelta(minutes=settings.MAX_CONFIRMATION_TTL_MINUTES)


class ConfirmationRule:
    """A single rule that can require confirmation."""

    def __init__(self, name: str, condition, reason: str):
        self.name = name
        self.condition = condition  # callable(schema, params, user) -> bool
        self.reason = reason


# ── Built-in Rules ──────────────────────────────────────

RULES: List[ConfirmationRule] = [
    ConfirmationRule(
        "high_risk",
        lambda schema, params, user: schema.risk_level
        in (RiskLevel.HIGH, RiskLevel.CRITICAL),
        "This action is classified as high-risk.",
    ),
    ConfirmationRule(
        "schema_requires",
        lambda schema, params, user: schema.requires_confirmation,
        "This action type always requires confirmation.",
    ),
    ConfirmationRule(
        "external_recipient",
        lambda schema, params, user: "recipient" in params
        and "@" in str(params.get("recipient", "")),
        "Action targets an external recipient.",
    ),
    ConfirmationRule(
        "destructive_filesystem",
        lambda schema, params, user: schema.action_type.startswith("filesystem.")
        and any(kw in str(params).lower() for kw in ["delete", "remove", "rmdir", "unlink"]),
        "Destructive file operation detected.",
    ),
    ConfirmationRule(
        "system_command",
        lambda schema, params, user: schema.action_type == "system.run_command",
        "System command execution requires explicit approval.",
    ),
]


class ConfirmationEngine:
    """Evaluate confirmation rules and manage confirmation tokens."""

    def evaluate(
        self, schema: ActionSchema, params: Dict[str, Any], user: dict
    ) -> Tuple[bool, List[str]]:
        """
        Evaluate all rules against an action.
        Returns (requires_confirmation, list_of_triggered_rule_reasons).
        """
        triggered = []
        for rule in RULES:
            try:
                if rule.condition(schema, params, user):
                    triggered.append(rule.reason)
            except Exception:
                pass  # Rule evaluation failures are non-fatal
        return len(triggered) > 0, triggered

    @staticmethod
    def generate_token() -> Tuple[str, str]:
        """
        Generate a confirmation token pair.
        Returns (raw_token_for_client, sha256_hash_for_storage).
        """
        raw = secrets.token_urlsafe(32)
        hashed = hashlib.sha256(raw.encode()).hexdigest()
        return raw, hashed

    @staticmethod
    def validate_token(raw_token: str, stored_hash: str, created_at: datetime) -> bool:
        """Validate a confirmation token: hash match + TTL check."""
        if datetime.utcnow() - created_at > CONFIRMATION_TTL:
            return False
        return hashlib.sha256(raw_token.encode()).hexdigest() == stored_hash

    @staticmethod
    def get_expiry_time() -> datetime:
        """Return the expiry timestamp for a new confirmation."""
        return datetime.utcnow() + CONFIRMATION_TTL
