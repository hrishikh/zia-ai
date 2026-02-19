"""Zia AI — Pending Confirmation Model"""
import uuid
from sqlalchemy import Column, String, DateTime, JSON, Uuid
from sqlalchemy.sql import func
from app.database import Base


class PendingConfirmation(Base):
    __tablename__ = "pending_confirmations"

    id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    user_id = Column(Uuid, nullable=False, index=True)
    execution_id = Column(String(100), unique=True, nullable=False, index=True)
    action_type = Column(String(100), nullable=False)
    action_preview = Column(JSON, default={})
    token_hash = Column(String(64), nullable=False)  # SHA-256
    triggered_rules = Column(JSON, default=[])
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=False)
    status = Column(String(20), default="pending")  # pending | confirmed | rejected | expired
