"""
Zia AI — Auth Service
OAuth2 token management: store, retrieve, refresh, revoke (with encryption).
"""

import logging
from datetime import datetime
from typing import Optional

import httpx
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.crypto import crypto
from app.models.oauth_token import OAuthToken
from app.models.connected_service import ConnectedService

logger = logging.getLogger("zia.auth")

REVOCATION_ENDPOINTS = {
    "gmail": "https://oauth2.googleapis.com/revoke",
    "spotify": "https://accounts.spotify.com/api/token",
}


class AuthService:
    """Manages OAuth2 tokens with encryption at rest."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def store_tokens(
        self,
        user_id: str,
        service: str,
        access_token: str,
        refresh_token: Optional[str],
        expires_at: Optional[datetime],
        scopes: list[str],
    ) -> None:
        """Encrypt and store OAuth tokens."""
        uid = str(user_id)
        token = OAuthToken(
            user_id=user_id,
            service=service,
            access_token_encrypted=crypto.encrypt(access_token, uid),
            refresh_token_encrypted=crypto.encrypt(refresh_token, uid) if refresh_token else None,
            expires_at=expires_at,
            scopes=scopes,
        )
        self.db.add(token)

        # Upsert connected service
        svc = ConnectedService(
            user_id=user_id,
            service_name=service,
            status="active",
        )
        self.db.add(svc)
        await self.db.flush()
        logger.info(f"Stored tokens for {service} (user={uid})")

    async def get_access_token(self, user_id: str, service: str) -> Optional[str]:
        """Retrieve and decrypt an access token."""
        result = await self.db.execute(
            select(OAuthToken).where(
                OAuthToken.user_id == user_id,
                OAuthToken.service == service,
            )
        )
        token = result.scalar_one_or_none()
        if not token:
            return None
        return crypto.decrypt(token.access_token_encrypted, str(user_id))

    async def revoke_service(self, user_id: str, service: str) -> bool:
        """Revoke OAuth tokens: call provider + delete from DB."""
        uid = str(user_id)
        access_token = await self.get_access_token(user_id, service)

        # Call provider revocation
        endpoint = REVOCATION_ENDPOINTS.get(service)
        if endpoint and access_token:
            try:
                async with httpx.AsyncClient() as client:
                    await client.post(endpoint, params={"token": access_token})
            except Exception as e:
                logger.warning(f"Revocation call failed for {service}: {e}")

        # Delete from DB
        await self.db.execute(
            delete(OAuthToken).where(
                OAuthToken.user_id == user_id,
                OAuthToken.service == service,
            )
        )
        await self.db.execute(
            delete(ConnectedService).where(
                ConnectedService.user_id == user_id,
                ConnectedService.service_name == service,
            )
        )
        await self.db.flush()
        logger.info(f"Revoked {service} for user {uid}")
        return True
