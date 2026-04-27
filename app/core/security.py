from datetime import datetime, timedelta, timezone
from typing import Annotated, Any, Optional

import jwt
from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.config import settings
from app.core.exceptions import AppException
from passlib.context import CryptContext
from pydantic import BaseModel

# bcrypt has a 72-byte password limit at the algorithm level.
# Use bcrypt_sha256 so long passphrases are pre-hashed safely.
_password_context = CryptContext(schemes=["bcrypt_sha256"], deprecated="auto")


def hash_password(plain: str) -> str:
    return _password_context.hash(plain)


def verify_password(plain: str, hashed: str) -> bool:
    return _password_context.verify(plain, hashed)


class AuthContext(BaseModel):
    user_id: str
    role_id: Optional[str] = None
    hub_id: Optional[str] = None


bearer_scheme = HTTPBearer(auto_error=False)


def create_access_token(
    *,
    user_id: str,
    role_id: Optional[str] = None,
    hub_id: Optional[str] = None,
    email: str = "",
    mobile_no: str = "",
    role_type: str = "",
) -> str:
    now = datetime.now(timezone.utc)
    expire = now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    payload: dict[str, Any] = {
        "sub": user_id,
        "role_id": role_id,
        "hub_id": hub_id,
        "email": email,
        "mobile_no": mobile_no,
        "role_type": role_type,
        "typ": "access",
        "iat": int(now.timestamp()),
        "exp": int(expire.timestamp()),
    }
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def create_refresh_token(
    *,
    user_id: str,
    role_id: Optional[str] = None,
    hub_id: Optional[str] = None,
    email: str = "",
    mobile_no: str = "",
    role_type: str = "",
) -> str:
    now = datetime.now(timezone.utc)
    expire = now + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    payload: dict[str, Any] = {
        "sub": user_id,
        "role_id": role_id,
        "hub_id": hub_id,
        "email": email,
        "mobile_no": mobile_no,
        "role_type": role_type,
        "typ": "refresh",
        "iat": int(now.timestamp()),
        "exp": int(expire.timestamp()),
    }
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def decode_token(token: str) -> dict[str, Any]:
    try:
        return jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
    except jwt.PyJWTError as e:
        raise AppException("Invalid token", status_code=401) from e


def decode_refresh_token(token: str) -> dict[str, Any]:
    payload = decode_token(token)
    if payload.get("typ") != "refresh":
        raise AppException("Invalid refresh token", status_code=401)
    return payload


def get_current_user(
    credentials: Annotated[Optional[HTTPAuthorizationCredentials], Depends(bearer_scheme)],
) -> AuthContext:
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise AppException("Not authenticated", status_code=401)
    try:
        payload = jwt.decode(
            credentials.credentials,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
    except jwt.PyJWTError:
        raise AppException("Could not validate credentials", status_code=401)
    if payload.get("typ") != "access":
        raise AppException("Invalid access token", status_code=401)
    sub = payload.get("sub")
    if not sub:
        raise AppException("Not authenticated", status_code=401)
    return AuthContext(
        user_id=str(sub),
        role_id=str(payload["role_id"]) if payload.get("role_id") else None,
        hub_id=str(payload["hub_id"]) if payload.get("hub_id") else None,
    )
