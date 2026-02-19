"""Zia AI — OAuth Token Model (encrypted at rest)"""
import uuid
from sqlalchemy import Column, String, SmallInteger, DateTime, Text, JSON, Uuid
from sqlalchemy.sql import func
from app.database import Base


class OAuthToken(Base):
    __tablename__ = "oauth_tokens"

    id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    user_id = Column(Uuid, nullable=False, index=True)
    service = Column(String(50), nullable=False)  # gmail | spotify
    access_token_encrypted = Column(Text, nullable=False)
    refresh_token_encrypted = Column(Text, nullable=True)
    expires_at = Column(DateTime(timezone=True), nullable=True)
    scopes = Column(JSON, default=[])
    key_version = Column(SmallInteger, default=1)  # Master key version
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
