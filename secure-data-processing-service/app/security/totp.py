from __future__ import annotations

import base64
import hashlib
import hmac
import secrets
import struct
import time


def generate_secret() -> str:
    return base64.b32encode(secrets.token_bytes(20)).decode("ascii").rstrip("=")


def _normalize(secret: str) -> bytes:
    padding = "=" * (-len(secret) % 8)
    return base64.b32decode(secret + padding, casefold=True)


def totp(secret: str, for_time: int | None = None, period: int = 30, digits: int = 6) -> str:
    if for_time is None:
        for_time = int(time.time())
    counter = int(for_time // period)
    msg = struct.pack(">Q", counter)
    mac = hmac.new(_normalize(secret), msg, hashlib.sha1).digest()
    offset = mac[-1] & 0x0F
    code = struct.unpack(">I", mac[offset:offset + 4])[0] & 0x7FFFFFFF
    return str(code % (10**digits)).zfill(digits)


def verify(secret: str, code: str, window: int = 1) -> bool:
    now = int(time.time())
    for delta in range(-window, window + 1):
        if totp(secret, now + (delta * 30)) == code:
            return True
    return False
