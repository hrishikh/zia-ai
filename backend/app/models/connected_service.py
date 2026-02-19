"""Zia AI — Connected Service Model"""
import uuid
from sqlalchemy import Column, String, DateTime, JSON, Uuid
from sqlalchemy.sql import func
from app.database import Base


class ConnectedService(Base):
    __tablename__ = "connected_services"

    id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    user_id = Column(Uuid, nullable=False, index=True)
    service_name = Column(String(50), nullable=False)
    status = Column(String(20), default="active")  # active | expired | revoked
    metadata_ = Column("metadata", JSON, default={})
    connected_at = Column(DateTime(timezone=True), server_default=func.now())
