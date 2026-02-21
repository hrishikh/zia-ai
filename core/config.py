"""
Centralized configuration — all secrets loaded from environment variables only.

Startup behavior:
  1. Resolves .env path relative to project root (parent of core/)
  2. If .env is missing, auto-copies .env.example as a starting point
  3. Loads .env via python-dotenv
  4. Prints which file was loaded (never prints key values)
"""

import os
import shutil
from pathlib import Path
from dotenv import load_dotenv

# ── Resolve paths relative to project root ──
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
_ENV_FILE = _PROJECT_ROOT / ".env"
_ENV_EXAMPLE = _PROJECT_ROOT / ".env.example"


def _bootstrap_env():
    """Ensure .env exists and load it."""
    if not _ENV_FILE.exists():
        if _ENV_EXAMPLE.exists():
            shutil.copy(_ENV_EXAMPLE, _ENV_FILE)
            print(f"📄 Created {_ENV_FILE} from .env.example")
            print("   ⚠️  Please fill in your GROQ_API_KEY and restart.")
        else:
            print(f"❌ No .env or .env.example found at {_PROJECT_ROOT}")
        return False

    loaded = load_dotenv(_ENV_FILE, override=True)
    if loaded:
        print(f"✅ Loaded config from: {_ENV_FILE}")
    else:
        print(f"⚠️  .env file found but no variables loaded: {_ENV_FILE}")
    return loaded


_bootstrap_env()


class Settings:
    """Read-only settings from environment variables."""

    # ── Groq ──
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    GROQ_MODEL: str = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

    # ── Gmail OAuth ──
    GMAIL_CLIENT_ID: str = os.getenv("GMAIL_CLIENT_ID", "")
    GMAIL_CLIENT_SECRET: str = os.getenv("GMAIL_CLIENT_SECRET", "")

    # ── Twilio ──
    TWILIO_ACCOUNT_SID: str = os.getenv("TWILIO_ACCOUNT_SID", "")
    TWILIO_AUTH_TOKEN: str = os.getenv("TWILIO_AUTH_TOKEN", "")
    TWILIO_PHONE_NUMBER: str = os.getenv("TWILIO_PHONE_NUMBER", "")
    TWILIO_WHATSAPP_NUMBER: str = os.getenv("TWILIO_WHATSAPP_NUMBER", "")

    # ── Spotify ──
    SPOTIFY_CLIENT_ID: str = os.getenv("SPOTIFY_CLIENT_ID", "")
    SPOTIFY_CLIENT_SECRET: str = os.getenv("SPOTIFY_CLIENT_SECRET", "")

    # ── Agent Behavior ──
    MAX_CONVERSATION_TURNS: int = int(os.getenv("MAX_CONVERSATION_TURNS", "20"))
    ALLOWED_DIRECTORIES: list = os.getenv(
        "ALLOWED_DIRECTORIES", r"D:\Zia AI;C:\Users"
    ).split(";")

    def validate(self) -> list[str]:
        """Return list of missing critical settings."""
        missing = []
        if not self.GROQ_API_KEY:
            missing.append("GROQ_API_KEY")
        return missing


settings = Settings()
