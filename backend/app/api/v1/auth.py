"""
Zia AI — Auth API
POST /register, /login, /refresh, /logout + OAuth service management.
"""

import uuid as _uuid
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.database import get_db
from app.models.user import User
from app.models.connected_service import ConnectedService as ConnectedServiceModel
from app.schemas.auth import (
    ConnectedServiceResponse,
    LoginRequest,
    RefreshRequest,
    RegisterRequest,
    TokenResponse,
    UserResponse,
)

router = APIRouter()


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(request: RegisterRequest, db: AsyncSession = Depends(get_db)):
    """Register a new user."""
    existing = await db.execute(select(User).where(User.email == request.email))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="Email already registered")

    user = User(
        email=request.email,
        password_hash=hash_password(request.password),
        display_name=request.display_name,
    )
    db.add(user)
    await db.flush()
    await db.refresh(user)

    return UserResponse(
        id=str(user.id), email=user.email, display_name=user.display_name,
        role=user.role, is_active=user.is_active, created_at=user.created_at,
        last_login=user.last_login,
    )


@router.post("/login", response_model=TokenResponse)
async def login(request: LoginRequest, db: AsyncSession = Depends(get_db)):
    """Login and receive JWT tokens."""
    result = await db.execute(select(User).where(User.email == request.email))
    user = result.scalar_one_or_none()

    if not user or not verify_password(request.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if not user.is_active:
        raise HTTPException(status_code=403, detail="Account disabled")

    user.last_login = datetime.utcnow()
    await db.flush()

    access = create_access_token(str(user.id), user.role)
    refresh = create_refresh_token(str(user.id))

    from app.config import settings
    return TokenResponse(
        access_token=access,
        refresh_token=refresh,
        expires_in=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(request: RefreshRequest, db: AsyncSession = Depends(get_db)):
    """Refresh an access token using a valid refresh token."""
    payload = decode_token(request.refresh_token)
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    user_id = payload["sub"]
    try:
        uid = _uuid.UUID(user_id)
    except (ValueError, AttributeError):
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    result = await db.execute(select(User).where(User.id == uid))
    user = result.scalar_one_or_none()
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="User not found")

    access = create_access_token(str(user.id), user.role)
    refresh = create_refresh_token(str(user.id))

    from app.config import settings
    return TokenResponse(
        access_token=access,
        refresh_token=refresh,
        expires_in=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


@router.post("/logout")
async def logout(user: dict = Depends(get_current_user)):
    """Logout — in production, blacklist the token in Redis."""
    return {"message": "Logged out", "user_id": user["id"]}


@router.get("/me", response_model=UserResponse)
async def get_me(user: dict = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """Get current user profile."""
    uid = _uuid.UUID(user["id"])
    result = await db.execute(select(User).where(User.id == uid))
    u = result.scalar_one_or_none()
    if not u:
        raise HTTPException(status_code=404, detail="User not found")
    return UserResponse(
        id=str(u.id), email=u.email, display_name=u.display_name,
        role=u.role, is_active=u.is_active, created_at=u.created_at,
        last_login=u.last_login,
    )


@router.get("/services", response_model=list[ConnectedServiceResponse])
async def get_services(
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List all connected OAuth services for the current user."""
    uid = _uuid.UUID(user["id"])
    result = await db.execute(
        select(ConnectedServiceModel).where(
            ConnectedServiceModel.user_id == uid,
            ConnectedServiceModel.status != "revoked",
        )
    )
    services = result.scalars().all()
    return [
        ConnectedServiceResponse(
            service=s.service_name,
            status=s.status,
            connected_at=s.connected_at,
            scopes=(s.metadata_ or {}).get("scopes", []),
        )
        for s in services
    ]


@router.delete("/services/{service_name}/revoke", status_code=204)
async def revoke_service(
    service_name: str,
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Revoke a connected OAuth service for the current user."""
    uid = _uuid.UUID(user["id"])
    result = await db.execute(
        select(ConnectedServiceModel).where(
            ConnectedServiceModel.user_id == uid,
            ConnectedServiceModel.service_name == service_name,
        )
    )
    service = result.scalar_one_or_none()
    if not service:
        raise HTTPException(status_code=404, detail=f"Service '{service_name}' not found")

    service.status = "revoked"
    await db.flush()
