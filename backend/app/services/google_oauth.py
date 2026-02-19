"""
Zia AI — Google OAuth 2.0 Helper (Stateless)
Builds auth URLs, exchanges codes, and fetches user info via httpx.
"""

from urllib.parse import urlencode

import httpx
from fastapi import HTTPException

from app.config import settings

GOOGLE_AUTH_ENDPOINT = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_ENDPOINT = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_ENDPOINT = "https://www.googleapis.com/oauth2/v2/userinfo"

SCOPES = "openid email profile"


def build_google_auth_url() -> str:
    """Construct the Google authorization URL for the OAuth 2.0 flow."""
    if not settings.GOOGLE_CLIENT_ID:
        raise RuntimeError("GOOGLE_CLIENT_ID not loaded from environment")
    params = {
        "client_id": settings.GOOGLE_CLIENT_ID,
        "redirect_uri": settings.GOOGLE_REDIRECT_URI,
        "response_type": "code",
        "scope": SCOPES,
        "access_type": "offline",
        "prompt": "consent",
    }
    return f"{GOOGLE_AUTH_ENDPOINT}?{urlencode(params)}"


async def exchange_code_for_tokens(code: str) -> dict:
    """Exchange an authorization code for Google tokens."""
    payload = {
        "client_id": settings.GOOGLE_CLIENT_ID,
        "client_secret": settings.GOOGLE_CLIENT_SECRET,
        "code": code,
        "grant_type": "authorization_code",
        "redirect_uri": settings.GOOGLE_REDIRECT_URI,
    }
    async with httpx.AsyncClient() as client:
        resp = await client.post(GOOGLE_TOKEN_ENDPOINT, data=payload)
        if resp.status_code != 200:
            raise HTTPException(
                status_code=502,
                detail=f"Google token exchange failed: {resp.text}",
            )
        return resp.json()


async def get_google_user_info(access_token: str) -> dict:
    """Fetch the authenticated Google user's profile information."""
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            GOOGLE_USERINFO_ENDPOINT,
            headers={"Authorization": f"Bearer {access_token}"},
        )
        if resp.status_code != 200:
            raise HTTPException(
                status_code=502,
                detail=f"Failed to fetch Google user info: {resp.text}",
            )
        data = resp.json()
        if not data.get("email"):
            raise HTTPException(
                status_code=400,
                detail="Google account has no email address",
            )
        return data
