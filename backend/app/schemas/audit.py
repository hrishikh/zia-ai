"""
Zia AI — Audit Schema Contracts
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel


class AuditLogEntry(BaseModel):
    id: str
    user_id: str
    action_type: str
    execution_id: str
    risk_level: str
    status: str
    source: str
    ip_address: Optional[str] = None
    created_at: datetime
    completed_at: Optional[datetime] = None
    duration_ms: Optional[int] = None
    message: Optional[str] = None


class AuditLogResponse(BaseModel):
    items: List[AuditLogEntry]
    total: int
    page: int
    per_page: int


class AuditStatsResponse(BaseModel):
    total_actions: int
    actions_today: int
    success_rate: float
    most_used_actions: Dict[str, int]
    risk_distribution: Dict[str, int]


class AuditExportRequest(BaseModel):
    format: str = "json"  # json | csv
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    action_types: Optional[List[str]] = None
