"""
Zia AI — Token Encryption Service
Envelope encryption: Master Key → per-user HKDF-derived DEK → Fernet ciphertext.
Supports key rotation via MultiFernet.
"""

import base64
import logging

from cryptography.fernet import Fernet, MultiFernet, InvalidToken
from cryptography.hazmat.primitives.hashes import SHA256
from cryptography.hazmat.primitives.kdf.hkdf import HKDF

from app.config import settings

logger = logging.getLogger("zia.crypto")


class TokenEncryptionService:
    """Envelope encryption with per-user key derivation and key rotation."""

    def __init__(self):
        raw_keys = settings.ENCRYPTION_KEY.split(",") if settings.ENCRYPTION_KEY else []
        if not raw_keys or not raw_keys[0].strip():
            logger.warning(
                "ENCRYPTION_KEY not set — generating ephemeral key. "
                "Tokens will NOT survive restarts!"
            )
            raw_keys = [Fernet.generate_key().decode()]

        self._fernets = [Fernet(k.strip().encode()) for k in raw_keys]
        self._multi = MultiFernet(self._fernets)
        self._primary_key_bytes = self._fernets[0]._signing_key  # noqa: access internal

    def _derive_user_key(self, user_id: str) -> Fernet:
        """Derive a per-user DEK via HKDF from the master key."""
        hkdf = HKDF(
            algorithm=SHA256(),
            length=32,
            salt=b"zia-user-token-v1",
            info=user_id.encode(),
        )
        derived = base64.urlsafe_b64encode(hkdf.derive(self._primary_key_bytes))
        return Fernet(derived)

    def encrypt(self, plaintext: str, user_id: str) -> str:
        """Encrypt a token for at-rest storage."""
        f = self._derive_user_key(user_id)
        return f.encrypt(plaintext.encode()).decode()

    def decrypt(self, ciphertext: str, user_id: str) -> str:
        """Decrypt a stored token."""
        f = self._derive_user_key(user_id)
        try:
            return f.decrypt(ciphertext.encode()).decode()
        except InvalidToken:
            raise ValueError("Failed to decrypt token — key mismatch or corruption")

    def rotate_ciphertext(self, ciphertext: str) -> str:
        """Re-encrypt a ciphertext under the newest master key (for key rotation)."""
        return self._multi.rotate(ciphertext.encode()).decode()


# Module-level singleton
crypto = TokenEncryptionService()
