from __future__ import annotations

from typing import Any

from app.core.config import settings

_client: Any = None


def get_redis():
    """Optional Redis for session cache; returns None if REDIS_URL unset."""
    global _client
    url = settings.REDIS_URL.strip()
    if not url:
        return None
    if _client is None:
        import redis

        _client = redis.Redis.from_url(url, decode_responses=True)
    return _client


def cache_session_key(user_id: str, device_id: str) -> str:
    return f"fsc:user_session:{user_id}:{device_id}"


def set_session_cache(user_id: str, device_id: str, ttl_seconds: int = 86400) -> None:
    r = get_redis()
    if r is None:
        return
    try:
        r.setex(cache_session_key(user_id, device_id), ttl_seconds, "1")
    except Exception:
        pass


def delete_session_cache(user_id: str, device_id: str) -> None:
    r = get_redis()
    if r is None:
        return
    try:
        r.delete(cache_session_key(user_id, device_id))
    except Exception:
        pass
