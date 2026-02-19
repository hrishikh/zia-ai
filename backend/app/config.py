"""
Zia AI — Application Configuration
Pydantic Settings with env-based loading.
"""

from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    # ── App ──
    APP_NAME: str = "Zia AI"
    DEBUG: bool = False
    SECRET_KEY: str = "CHANGE-ME-IN-PRODUCTION"
    ALLOWED_HOSTS: List[str] = ["zia.yourdomain.com", "localhost", "127.0.0.1"]
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "https://zia.yourdomain.com",
    ]

    # ── Database ──
    DATABASE_URL: str = "postgresql+asyncpg://zia:password@localhost:5432/zia_db"

    # ── Redis ──
    REDIS_URL: str = "redis://localhost:6379/0"

    # ── JWT ──
    JWT_SECRET: str = "CHANGE-ME-JWT-SECRET"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # ── OAuth — Gmail ──
    GMAIL_CLIENT_ID: str = ""
    GMAIL_CLIENT_SECRET: str = ""
    GMAIL_REDIRECT_URI: str = "http://localhost:8000/api/v1/oauth/gmail/callback"

    # ── OAuth — Spotify ──
    SPOTIFY_CLIENT_ID: str = ""
    SPOTIFY_CLIENT_SECRET: str = ""

    # ── Twilio ──
    TWILIO_ACCOUNT_SID: str = ""
    TWILIO_AUTH_TOKEN: str = ""
    TWILIO_PHONE_NUMBER: str = ""
    TWILIO_WHATSAPP_NUMBER: str = ""

    # ── Security ──
    RATE_LIMIT_PER_MINUTE: int = 60
    MAX_CONFIRMATION_TTL_MINUTES: int = 5
    ENCRYPTION_KEY: str = ""  # Fernet key(s), comma-separated for rotation

    # ── Worker ──
    WORKER_MAX_JOBS: int = 10
    WORKER_JOB_TIMEOUT: int = 300

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
