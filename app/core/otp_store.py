from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone

from app.core.config import settings
from app.core.redis_cache import get_redis

_mem: dict[str, dict] = {}


def _key(session_info: str) -> str:
    return f"fsc:otp:{session_info}"


def create_session(phone_number: str) -> str:
    session_info = str(uuid.uuid4())
    payload = {
        "phone_number": phone_number,
        "code": settings.OTP_STATIC_CODE,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    r = get_redis()
    if r is not None:
        try:
            r.setex(_key(session_info), settings.OTP_TTL_SECONDS, json.dumps(payload))
            return session_info
        except Exception:
            pass
    _mem[session_info] = payload
    return session_info


def consume_session(session_info: str, otp: str) -> str | None:
    """Return phone number if otp matches, else None. Consumes the session."""
    r = get_redis()
    raw = None
    if r is not None:
        try:
            raw = r.get(_key(session_info))
        except Exception:
            raw = None
    if raw:
        try:
            payload = json.loads(raw)
        except Exception:
            return None
        if str(payload.get("code")) != str(otp):
            return None
        try:
            r.delete(_key(session_info))
        except Exception:
            pass
        return str(payload.get("phone_number") or "")

    payload = _mem.get(session_info)
    if not payload:
        return None
    if str(payload.get("code")) != str(otp):
        return None
    del _mem[session_info]
    return str(payload.get("phone_number") or "")

