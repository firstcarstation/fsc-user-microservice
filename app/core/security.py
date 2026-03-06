from datetime import datetime, timedelta, timezone
from typing import Annotated, List, Optional

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from passlib.context import CryptContext
from pydantic import BaseModel

from app.core.config import settings

_password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(plain: str) -> str:
    return _password_context.hash(plain)


def verify_password(plain: str, hashed: str) -> bool:
    return _password_context.verify(plain, hashed)


class AuthContext(BaseModel):
    user_id: str
    role_id: Optional[str] = None
    hub_id: Optional[str] = None


bearer_scheme = HTTPBearer(auto_error=False)


def create_access_token(subject: str, role_id: Optional[str] = None, hub_id: Optional[str] = None) -> str:
    now = datetime.now(timezone.utc)
    expire = now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {"sub": subject, "role_id": role_id, "hub_id": hub_id, "iat": int(now.timestamp()), "exp": int(expire.timestamp())}
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def get_auth_context(
    credentials: Annotated[Optional[HTTPAuthorizationCredentials], Depends(bearer_scheme)]
) -> AuthContext:
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    try:
        payload = jwt.decode(credentials.credentials, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
    except jwt.PyJWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials")
    sub = payload.get("sub")
    if not sub:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing subject")
    return AuthContext(
        user_id=str(sub),
        role_id=str(payload["role_id"]) if payload.get("role_id") else None,
        hub_id=str(payload["hub_id"]) if payload.get("hub_id") else None,
    )
