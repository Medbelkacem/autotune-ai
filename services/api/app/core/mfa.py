"""TOTP (RFC 6238) — enrollment and verification."""

from __future__ import annotations

import base64
import hashlib
import hmac
import os
import struct
import time
from urllib.parse import quote

_DIGITS = 6
_PERIOD = 30
_ALGO = hashlib.sha1
_WINDOW = 1   # accept ±1 period (30s) drift


def new_secret() -> bytes:
    return os.urandom(20)


def _hotp(secret: bytes, counter: int) -> str:
    b = struct.pack(">Q", counter)
    h = hmac.new(secret, b, _ALGO).digest()
    off = h[-1] & 0x0F
    binary = (
        ((h[off] & 0x7F) << 24)
        | ((h[off + 1] & 0xFF) << 16)
        | ((h[off + 2] & 0xFF) << 8)
        | (h[off + 3] & 0xFF)
    )
    return str(binary % 10**_DIGITS).zfill(_DIGITS)


def totp_now(secret: bytes, *, at: int | None = None) -> str:
    counter = (at or int(time.time())) // _PERIOD
    return _hotp(secret, counter)


def totp_verify(secret: bytes, code: str, *, at: int | None = None) -> bool:
    if not code or not code.strip().isdigit() or len(code.strip()) != _DIGITS:
        return False
    now = (at or int(time.time())) // _PERIOD
    for delta in range(-_WINDOW, _WINDOW + 1):
        if hmac.compare_digest(_hotp(secret, now + delta), code.strip()):
            return True
    return False


def provisioning_uri(*, email: str, issuer: str, secret: bytes) -> str:
    """Returns an otpauth:// URI suitable for QR-encoding in the client."""
    b32 = base64.b32encode(secret).decode().rstrip("=")
    label = quote(f"{issuer}:{email}")
    return (
        f"otpauth://totp/{label}?"
        f"secret={b32}&issuer={quote(issuer)}&algorithm=SHA1&digits={_DIGITS}&period={_PERIOD}"
    )
