import json
import logging
from typing import Any

try:
    import redis
except Exception:  # pragma: no cover - import guard for environments without optional deps
    redis = None

from app.core.config import settings

logger = logging.getLogger(__name__)


def get_redis_client():
    if redis is None:
        return None
    try:
        return redis.Redis.from_url(settings.redis_url, decode_responses=True)
    except Exception as exc:
        logger.warning("Redis connection unavailable: %s", exc)
        return None


def set_latest_risk(ad_id: str, payload: dict[str, Any]) -> None:
    client = get_redis_client()
    if not client:
        return
    try:
        client.set(f"ad:risk:{ad_id}", json.dumps(payload), ex=3600)
    except Exception as exc:
        logger.warning("Failed to cache risk score for %s: %s", ad_id, exc)


def get_latest_risk(ad_id: str) -> dict[str, Any] | None:
    client = get_redis_client()
    if not client:
        return None
    try:
        raw = client.get(f"ad:risk:{ad_id}")
        return json.loads(raw) if raw else None
    except Exception as exc:
        logger.warning("Failed to fetch risk score for %s: %s", ad_id, exc)
        return None
