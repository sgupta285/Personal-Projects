import hashlib
import hmac
from datetime import datetime, timedelta, timezone
from jose import jwt
from app.core.config import Settings


def hash_api_key(api_key: str) -> str:
    return hashlib.sha256(api_key.encode()).hexdigest()


def verify_api_key(api_key: str, api_key_hash: str | None) -> bool:
    if not api_key_hash:
        return False
    candidate = hashlib.sha256(api_key.encode()).hexdigest()
    return hmac.compare_digest(candidate, api_key_hash)


def create_access_token(subject: str, scopes: list[str], token_type: str, settings: Settings) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        'sub': subject,
        'scope': ' '.join(scopes),
        'token_type': token_type,
        'iat': int(now.timestamp()),
        'exp': int((now + timedelta(minutes=settings.access_token_ttl_minutes)).timestamp()),
        'jti': hashlib.sha256(f'{subject}:{now.timestamp()}'.encode()).hexdigest()[:24],
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)
