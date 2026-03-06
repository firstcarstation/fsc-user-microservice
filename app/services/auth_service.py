from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import create_access_token, verify_password
from app.crud.query.user_query import get_user_by_mobile
from app.models.user_model import User
from app.schemas.auth_schema import LoginRequest, TokenResponse


def login(db: Session, payload: LoginRequest) -> TokenResponse:
    user = get_user_by_mobile(db, payload.mobile_no)
    if user is None or (user.password_hash and not verify_password(payload.password, user.password_hash)):
        raise ValueError("Invalid credentials")
    token = create_access_token(subject=user.user_id, role_id=user.role_id, hub_id=user.hub_id)
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return TokenResponse(
        access_token=token,
        expires_at=expires_at,
        user_id=user.user_id,
        role_id=user.role_id,
        hub_id=user.hub_id,
    )
