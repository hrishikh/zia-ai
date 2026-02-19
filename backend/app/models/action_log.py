"""Zia AI — Action Log Model"""
import uuid
from sqlalchemy import Column, String, Integer, DateTime, Text, JSON, Uuid
from sqlalchemy.sql import func
from app.database import Base


class ActionLog(Base):
    __tablename__ = "action_logs"

    id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    user_id = Column(Uuid, nullable=False, index=True)
    action_type = Column(String(100), nullable=False, index=True)
    execution_id = Column(String(100), unique=True, nullable=False, index=True)
    params = Column(JSON, default={})  # Sensitive fields redacted
    risk_level = Column(String(20), nullable=False)
    status = Column(String(30), nullable=False, index=True)
    source = Column(String(20), default="text")  # voice | text | api | macro
    result = Column(JSON, nullable=True)
    error = Column(Text, nullable=True)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(500), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    duration_ms = Column(Integer, nullable=True)
    state_history = Column(JSON, default=[])  # FSM transitions
