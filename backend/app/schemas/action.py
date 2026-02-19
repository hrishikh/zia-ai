"""
Zia AI — Action Schema Contracts
Defines the core data models for the action system.
"""

import uuid
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, Field


# ── Enums ──────────────────────────────────────────────


class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ActionStatus(str, Enum):
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


# ── Request / Response Models ───────────────────────────


class ActionRequest(BaseModel):
    """Incoming action request from the client."""
    input_text: Optional[str] = None
    action_type: Optional[str] = None
    params: Optional[Dict[str, Any]] = None
    source: Literal["voice", "text", "api", "macro"] = "text"


class ActionResponse(BaseModel):
    """Response returned to the client after action submission."""
    execution_id: str
    status: ActionStatus
    message: str
    data: Optional[Dict[str, Any]] = None
    confirmation_required: bool = False
    confirmation_token: Optional[str] = None
    action_preview: Optional[Dict[str, Any]] = None


class ConfirmActionRequest(BaseModel):
    """Request to confirm a pending action."""
    execution_id: str
    confirmation_token: str


class RejectActionRequest(BaseModel):
    """Request to reject a pending action."""
    execution_id: str
    reason: Optional[str] = None


class ActionHistoryItem(BaseModel):
    """Single item in action history listing."""
    execution_id: str
    action_type: str
    status: ActionStatus
    source: str
    risk_level: RiskLevel
    created_at: datetime
    completed_at: Optional[datetime] = None
    duration_ms: Optional[int] = None
    message: Optional[str] = None


class ActionHistoryResponse(BaseModel):
    """Paginated action history."""
    items: List[ActionHistoryItem]
    total: int
    page: int
    per_page: int


# ── Action Schema Definition ───────────────────────────


class ActionSchema(BaseModel):
    """Registered action definition used by the ActionRegistry."""
    action_type: str
    display_name: str
    description: str
    risk_level: RiskLevel
    requires_confirmation: bool
    required_params: List[str]
    optional_params: List[str] = []
    executor: str
    cooldown_seconds: int = 0
    max_daily_executions: int = 0  # 0 = unlimited
    allowed_roles: List[str] = ["user", "admin"]


# ── Internal Execution Record ──────────────────────────


class ActionExecution(BaseModel):
    """Internal record tracking an action through its lifecycle."""
    execution_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    action_type: str
    params: Dict[str, Any]
    risk_level: RiskLevel
    status: ActionStatus = ActionStatus.CREATED
    confirmation_token_hash: Optional[str] = None
    user_id: str
    source: str = "text"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    executed_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
