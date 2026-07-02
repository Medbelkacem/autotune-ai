"""Password hashing, JWT, and ed25519 signing for recommendation bundles."""

from __future__ import annotations

import base64
import secrets
from datetime import datetime, timedelta, timezone
from typing import Any
from uuid import UUID

import nacl.signing
from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import get_settings

_pwd_ctx = CryptContext(schemes=["argon2"], deprecated="auto")
_settings = get_settings()


# ─── Passwords ──────────────────────────────────────────────────────────

def hash_password(plain: str) -> str:
    """Argon2id with a pepper. Pepper is global; salt is per-hash by argon2."""
    return _pwd_ctx.hash(plain + _settings.password_pepper)


def verify_password(plain: str, hashed: str) -> bool:
    try:
        return _pwd_ctx.verify(plain + _settings.password_pepper, hashed)
    except Exception:
        return False


# ─── JWT ─────────────────────────────────────────────────────────────────

ALGO = "HS256"  # for local dev; production uses RS256/ES256 with KMS


def create_access_token(
    *,
    subject: str | UUID,
    org_id: str | UUID,
    roles: list[str],
    extra: dict[str, Any] | None = None,
) -> str:
    now = datetime.now(timezone.utc)
    payload: dict[str, Any] = {
        "iss": _settings.jwt_issuer,
        "aud": _settings.jwt_audience,
        "sub": str(subject),
        "org": str(org_id),
        "roles": roles,
        "iat": int(now.timestamp()),
        "nbf": int(now.timestamp()),
        "exp": int((now + timedelta(seconds=_settings.jwt_access_ttl_seconds)).timestamp()),
        "jti": secrets.token_urlsafe(16),
        "typ": "access",
    }
    if extra:
        payload.update(extra)
    return jwt.encode(payload, _settings.secret_key, algorithm=ALGO)


def create_refresh_token(*, subject: str | UUID) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "iss": _settings.jwt_issuer,
        "sub": str(subject),
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(seconds=_settings.jwt_refresh_ttl_seconds)).timestamp()),
        "jti": secrets.token_urlsafe(24),
        "typ": "refresh",
    }
    return jwt.encode(payload, _settings.secret_key, algorithm=ALGO)


def decode_token(token: str, *, expected_type: str = "access") -> dict[str, Any]:
    try:
        payload = jwt.decode(
            token,
            _settings.secret_key,
            algorithms=[ALGO],
            audience=_settings.jwt_audience if expected_type == "access" else None,
            issuer=_settings.jwt_issuer,
        )
    except JWTError as exc:
        raise ValueError(f"invalid token: {exc}") from exc
    if payload.get("typ") != expected_type:
        raise ValueError(f"wrong token type (expected {expected_type})")
    return payload


# ─── ed25519 signing (recommendation bundles) ───────────────────────────

def generate_signing_key() -> tuple[str, str]:
    """Returns (private_b64, public_b64)."""
    sk = nacl.signing.SigningKey.generate()
    return (
        base64.b64encode(bytes(sk)).decode(),
        base64.b64encode(bytes(sk.verify_key)).decode(),
    )


def sign_blob(blob: bytes, private_b64: str) -> str:
    sk = nacl.signing.SigningKey(base64.b64decode(private_b64))
    return base64.b64encode(sk.sign(blob).signature).decode()


def verify_signature(blob: bytes, signature_b64: str, public_b64: str) -> bool:
    try:
        vk = nacl.signing.VerifyKey(base64.b64decode(public_b64))
        vk.verify(blob, base64.b64decode(signature_b64))
        return True
    except Exception:
        return False


def fingerprint(public_b64: str) -> str:
    import hashlib
    return hashlib.sha256(base64.b64decode(public_b64)).hexdigest()[:16]
