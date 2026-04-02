from __future__ import annotations

import hashlib
import hmac
import secrets
from datetime import datetime, timedelta, timezone
from typing import Any

import jwt

from app.config import settings
from app.database import execute, fetch_one, now_iso
from app.models import UserContext
from app.security.totp import generate_secret, verify


PBKDF2_ROUNDS = 240_000


def hash_password(password: str, salt: bytes | None = None) -> str:
    salt = salt or secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, PBKDF2_ROUNDS)
    return f"{salt.hex()}${digest.hex()}"


def verify_password(password: str, stored: str) -> bool:
    salt_hex, digest_hex = stored.split("$", 1)
    expected = hash_password(password, bytes.fromhex(salt_hex))
    return hmac.compare_digest(expected, stored)


def create_access_token(user: UserContext) -> str:
    expires = datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_ttl_minutes)
    payload: dict[str, Any] = {
        "sub": user.username,
        "role": user.role,
        "org_id": user.org_id,
        "allowed_tags": user.allowed_tags,
        "exp": expires,
        "iat": datetime.now(timezone.utc),
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def decode_access_token(token: str) -> UserContext:
    payload = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
    return UserContext(
        username=payload["sub"],
        role=payload["role"],
        org_id=payload["org_id"],
        allowed_tags=list(payload.get("allowed_tags", [])),
    )


def get_user_by_username(username: str):
    return fetch_one("SELECT * FROM users WHERE username = ? AND is_active = 1", (username,))


def authenticate_user(username: str, password: str, mfa_code: str | None = None) -> UserContext | None:
    row = get_user_by_username(username)
    if not row or not verify_password(password, row["password_hash"]):
        return None
    if row["can_use_mfa"] and not (mfa_code and verify(row["mfa_secret"], mfa_code)):
        return None
    return UserContext(
        username=row["username"],
        role=row["role"],
        org_id=row["org_id"],
        allowed_tags=[],
    )


def create_user(username: str, password: str, role: str, org_id: str) -> str:
    secret = generate_secret()
    execute(
        "INSERT INTO users (username, password_hash, role, org_id, mfa_secret, created_at) VALUES (?, ?, ?, ?, ?, ?)",
        (username, hash_password(password), role, org_id, secret, now_iso()),
    )
    return secret
