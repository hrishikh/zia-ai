"""
Zia AI — Auth Schema Contracts
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    display_name: Optional[str] = Field(None, max_length=100)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds


class RefreshRequest(BaseModel):
    refresh_token: str


class UserResponse(BaseModel):
    id: str
    email: str
    display_name: Optional[str]
    role: str
    is_active: bool
    created_at: datetime
    last_login: Optional[datetime]


class OAuthAuthorizeResponse(BaseModel):
    authorization_url: str
    state: str


class ConnectedServiceResponse(BaseModel):
    service: str
    status: str  # active | expired | revoked
    connected_at: Optional[datetime]
    scopes: list[str] = []
