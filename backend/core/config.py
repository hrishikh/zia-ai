"""
Zia Core Config — Bridge to backend app.config.settings.

When running inside the FastAPI backend, this module reads from
app.config.settings (Pydantic) instead of its own dotenv.
When running standalone (CLI mode via root main.py), it loads its own .env.
"""

import os
from pathlib import Path

# Try to import from FastAPI backend config first
try:
    from app.config import settings as _app_settings

    class Settings:
        GROQ_API_KEY: str = _app_settings.GROQ_API_KEY
        GROQ_MODEL: str = _app_settings.GROQ_MODEL
        GMAIL_CLIENT_ID: str = _app_settings.GMAIL_CLIENT_ID
        GMAIL_CLIENT_SECRET: str = _app_settings.GMAIL_CLIENT_SECRET
        TWILIO_ACCOUNT_SID: str = getattr(_app_settings, "TWILIO_ACCOUNT_SID", "")
        TWILIO_AUTH_TOKEN: str = getattr(_app_settings, "TWILIO_AUTH_TOKEN", "")
        TWILIO_PHONE_NUMBER: str = getattr(_app_settings, "TWILIO_PHONE_NUMBER", "")
        TWILIO_WHATSAPP_NUMBER: str = getattr(_app_settings, "TWILIO_WHATSAPP_NUMBER", "")
        SPOTIFY_CLIENT_ID: str = getattr(_app_settings, "SPOTIFY_CLIENT_ID", "")
        SPOTIFY_CLIENT_SECRET: str = getattr(_app_settings, "SPOTIFY_CLIENT_SECRET", "")
        MAX_CONVERSATION_TURNS: int = 20
        ALLOWED_DIRECTORIES: list = os.getenv(
            "ALLOWED_DIRECTORIES", r"D:\Zia AI;C:\Users"
        ).split(";")

        def validate(self) -> list[str]:
            missing = []
            if not self.GROQ_API_KEY:
                missing.append("GROQ_API_KEY")
            return missing

    settings = Settings()

except ImportError:
    # Standalone mode — use dotenv
    import shutil
    from dotenv import load_dotenv

    _PROJECT_ROOT = Path(__file__).resolve().parent.parent
    _ENV_FILE = _PROJECT_ROOT / ".env"
    _ENV_EXAMPLE = _PROJECT_ROOT / ".env.example"

    def _bootstrap_env():
        if not _ENV_FILE.exists():
            if _ENV_EXAMPLE.exists():
                shutil.copy(_ENV_EXAMPLE, _ENV_FILE)
                print(f"📄 Created {_ENV_FILE} from .env.example")
            else:
                print(f"❌ No .env or .env.example found at {_PROJECT_ROOT}")
            return False
        loaded = load_dotenv(_ENV_FILE, override=True)
        if loaded:
            print(f"✅ Loaded config from: {_ENV_FILE}")
        return loaded

    _bootstrap_env()

    class Settings:
        GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
        GROQ_MODEL: str = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
        GMAIL_CLIENT_ID: str = os.getenv("GMAIL_CLIENT_ID", "")
        GMAIL_CLIENT_SECRET: str = os.getenv("GMAIL_CLIENT_SECRET", "")
        TWILIO_ACCOUNT_SID: str = os.getenv("TWILIO_ACCOUNT_SID", "")
        TWILIO_AUTH_TOKEN: str = os.getenv("TWILIO_AUTH_TOKEN", "")
        TWILIO_PHONE_NUMBER: str = os.getenv("TWILIO_PHONE_NUMBER", "")
        TWILIO_WHATSAPP_NUMBER: str = os.getenv("TWILIO_WHATSAPP_NUMBER", "")
        SPOTIFY_CLIENT_ID: str = os.getenv("SPOTIFY_CLIENT_ID", "")
        SPOTIFY_CLIENT_SECRET: str = os.getenv("SPOTIFY_CLIENT_SECRET", "")
        MAX_CONVERSATION_TURNS: int = int(os.getenv("MAX_CONVERSATION_TURNS", "20"))
        ALLOWED_DIRECTORIES: list = os.getenv(
            "ALLOWED_DIRECTORIES", r"D:\Zia AI;C:\Users"
        ).split(";")

        def validate(self) -> list[str]:
            missing = []
            if not self.GROQ_API_KEY:
                missing.append("GROQ_API_KEY")
            return missing

    settings = Settings()
