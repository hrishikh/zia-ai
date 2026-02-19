"""
Zia AI — Confirmation State Machine
Formal FSM with 13 states, enforced transitions, and history tracking.
"""

from enum import Enum
from datetime import datetime
from typing import List, Tuple


class ConfirmationState(str, Enum):
    CREATED = "created"
    RULES_EVAL = "rules_eval"
    AUTO_APPROVED = "auto_approved"
    PENDING = "pending_confirmation"
    CONFIRMED = "confirmed"
    REJECTED = "rejected"
    EXPIRED = "expired"
    ESCALATED = "escalated"
    QUEUED = "queued"
    EXECUTING = "executing"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRYING = "retrying"


# Valid transitions: current_state → set of allowed next states
TRANSITIONS: dict[ConfirmationState, set[ConfirmationState]] = {
    ConfirmationState.CREATED: {
        ConfirmationState.RULES_EVAL,
    },
    ConfirmationState.RULES_EVAL: {
        ConfirmationState.AUTO_APPROVED,
        ConfirmationState.PENDING,
    },
    ConfirmationState.AUTO_APPROVED: {
        ConfirmationState.QUEUED,
    },
    ConfirmationState.PENDING: {
        ConfirmationState.CONFIRMED,
        ConfirmationState.REJECTED,
        ConfirmationState.EXPIRED,
        ConfirmationState.ESCALATED,
    },
    ConfirmationState.ESCALATED: {
        ConfirmationState.CONFIRMED,
        ConfirmationState.REJECTED,
    },
    ConfirmationState.CONFIRMED: {
        ConfirmationState.QUEUED,
    },
    ConfirmationState.QUEUED: {
        ConfirmationState.EXECUTING,
    },
    ConfirmationState.EXECUTING: {
        ConfirmationState.COMPLETED,
        ConfirmationState.FAILED,
        ConfirmationState.RETRYING,
    },
    ConfirmationState.RETRYING: {
        ConfirmationState.EXECUTING,
        ConfirmationState.FAILED,
    },
    # Terminal states: REJECTED, EXPIRED, COMPLETED, FAILED — no outgoing transitions
}


class IllegalTransition(Exception):
    """Raised when an invalid state transition is attempted."""
    pass


class ActionStateMachine:
    """Enforces valid state transitions for an action's lifecycle."""

    def __init__(self, current_state: ConfirmationState = ConfirmationState.CREATED):
        self.state = current_state
        self.history: List[Tuple[ConfirmationState, ConfirmationState, str, datetime]] = []

    def transition(self, target: ConfirmationState, reason: str = "") -> None:
        """Attempt a state transition. Raises IllegalTransition if invalid."""
        allowed = TRANSITIONS.get(self.state, set())
        if target not in allowed:
            raise IllegalTransition(
                f"Cannot transition {self.state.value} → {target.value}. "
                f"Allowed: {[s.value for s in allowed]}"
            )
        self.history.append((self.state, target, reason, datetime.utcnow()))
        self.state = target

    @property
    def is_terminal(self) -> bool:
        """Check if the current state is terminal (no outgoing transitions)."""
        return self.state not in TRANSITIONS

    @property
    def is_awaiting_confirmation(self) -> bool:
        return self.state in (ConfirmationState.PENDING, ConfirmationState.ESCALATED)

    def get_history_log(self) -> list[dict]:
        """Return history as serializable dicts."""
        return [
            {
                "from": h[0].value,
                "to": h[1].value,
                "reason": h[2],
                "timestamp": h[3].isoformat(),
            }
            for h in self.history
        ]
