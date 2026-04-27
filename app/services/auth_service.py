from __future__ import annotations

from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from app.core.exceptions import AppException
from app.core.redis_cache import delete_session_cache, set_session_cache
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_refresh_token,
    hash_password,
    verify_password,
)
from app.crud.command.login_command import update_login
from app.crud.query.login_query import get_login_by_refresh_token, get_login_by_user_and_device
from app.crud.query.role_query import get_role_by_type
from app.crud.query.user_query import get_user_by_id, get_user_by_mobile
from app.models.enums import RoleTypeEnum, UserStatusEnum
from app.models.login_model import Login
from app.models.person_model import Person
from app.models.role_model import Role
from app.models.user_model import User
from app.schemas.auth_schema import (
    IsUserRegisteredRequest,
    LoginRequest,
    LogoutRequest,
    RefreshTokenRequest,
    RefreshTokenResponse,
    RegisterRequest,
    SendOtpRequest,
    SendOtpResponse,
    VerifyOtpRequest,
)
from app.schemas.user_schema import UserProfileResponse
from app.services.user_service import build_profile_response
from app.core.otp_store import consume_session, create_session


def _access_expires_at() -> datetime:
    from app.core.config import settings

    return datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)


def _role_type_value(db: Session, role_id: str) -> str:
    role = db.query(Role).filter(Role.role_id == role_id).first()
    return role.role_type.value if role else ""


def register_user(db: Session, payload: RegisterRequest) -> UserProfileResponse:
    if get_user_by_mobile(db, payload.mobile_no):
        raise AppException("User already registered", status_code=400)
    try:
        role_type = RoleTypeEnum(payload.role_type)
    except ValueError as e:
        raise AppException("Invalid role_type", status_code=400) from e
    # Public signup is customer-only. Staff/recovery accounts must be created by an admin.
    if role_type != RoleTypeEnum.CUSTOMER:
        raise AppException("Forbidden", status_code=403)
    role = get_role_by_type(db, role_type)
    if role is None:
        raise AppException("Roles not configured; run database migrations", status_code=500)

    person = Person(full_name=payload.full_name, email=payload.email)
    user = User(
        mobile_no=payload.mobile_no,
        password_hash=hash_password(payload.password),
        city=payload.city,
        role_id=role.role_id,
        status=UserStatusEnum.ACTIVE,
        hub_id=payload.hub_id,
        person_id=None,
    )
    try:
        db.add(person)
        db.flush()
        user.person_id = person.person_id
        db.add(user)
        db.flush()
        rt = _role_type_value(db, user.role_id)
        access = create_access_token(
            user_id=user.user_id,
            role_id=user.role_id,
            hub_id=user.hub_id,
            email=person.email,
            mobile_no=user.mobile_no,
            role_type=rt,
        )
        refresh = create_refresh_token(
            user_id=user.user_id,
            role_id=user.role_id,
            hub_id=user.hub_id,
            email=person.email,
            mobile_no=user.mobile_no,
            role_type=rt,
        )
        login_row = Login(
            user_id=user.user_id,
            device_id=payload.device_id,
            fcm_token=payload.fcm_token,
            device_type=payload.device_type,
            ip_address=payload.ip_address,
            token=access,
            refresh_token=refresh,
            is_logout=False,
        )
        db.add(login_row)
        db.commit()
        db.refresh(user)
        db.refresh(person)
    except Exception:
        db.rollback()
        raise

    set_session_cache(user.user_id, payload.device_id)
    exp = _access_expires_at()
    return build_profile_response(
        db,
        user,
        access_token=access,
        refresh_token=refresh,
        expires_at=exp,
    )


def _assert_admin(db: Session, user_id: str) -> None:
    user = db.query(User).filter(User.user_id == user_id).first()
    if user is None:
        raise AppException("Not authenticated", status_code=401)
    role = db.query(Role).filter(Role.role_id == user.role_id).first()
    rt = role.role_type.value if role else ""
    if rt not in ("admin", "hub_manager"):
        raise AppException("Admin only", status_code=403)


def admin_create_staff(db: Session, *, admin_user_id: str, payload: RegisterRequest) -> dict[str, str]:
    """Admin-only creation of staff/recovery users without switching admin session."""
    _assert_admin(db, admin_user_id)
    if get_user_by_mobile(db, payload.mobile_no):
        raise AppException("User already registered", status_code=400)
    try:
        role_type = RoleTypeEnum(payload.role_type)
    except ValueError as e:
        raise AppException("Invalid role_type", status_code=400) from e
    # Only recovery agents have logins; other operational assignments are handled in Order MS as lookup data.
    if role_type != RoleTypeEnum.AGENT:
        raise AppException("Invalid staff role_type", status_code=400)
    role = get_role_by_type(db, role_type)
    if role is None:
        raise AppException("Roles not configured; run database migrations", status_code=500)

    person = Person(full_name=payload.full_name, email=payload.email)
    user = User(
        mobile_no=payload.mobile_no,
        password_hash=hash_password(payload.password),
        city=payload.city,
        role_id=role.role_id,
        status=UserStatusEnum.ACTIVE,
        hub_id=payload.hub_id,
        person_id=None,
    )
    try:
        db.add(person)
        db.flush()
        user.person_id = person.person_id
        db.add(user)
        db.flush()
        db.commit()
        db.refresh(user)
    except Exception:
        db.rollback()
        raise
    return {"user_id": str(user.user_id)}


def login_user(db: Session, payload: LoginRequest) -> UserProfileResponse:
    user = get_user_by_mobile(db, payload.mobile_no)
    if user is None or not user.password_hash:
        raise AppException("Invalid credentials", status_code=401)
    if not verify_password(payload.password, user.password_hash):
        raise AppException("Invalid credentials", status_code=401)

    person = db.query(Person).filter(Person.person_id == user.person_id).first() if user.person_id else None
    email = person.email if person else ""
    rt = _role_type_value(db, user.role_id)
    access = create_access_token(
        user_id=user.user_id,
        role_id=user.role_id,
        hub_id=user.hub_id,
        email=email,
        mobile_no=user.mobile_no,
        role_type=rt,
    )
    refresh = create_refresh_token(
        user_id=user.user_id,
        role_id=user.role_id,
        hub_id=user.hub_id,
        email=email,
        mobile_no=user.mobile_no,
        role_type=rt,
    )
    exp = _access_expires_at()

    existing = get_login_by_user_and_device(db, user.user_id, payload.device_id)
    if existing:
        existing.token = access
        existing.refresh_token = refresh
        existing.login_at = datetime.now(timezone.utc)
        existing.fcm_token = payload.fcm_token
        existing.device_type = payload.device_type
        existing.ip_address = payload.ip_address
        existing.is_logout = False
        existing.logout_at = None
        update_login(db, existing)
    else:
        login_row = Login(
            user_id=user.user_id,
            device_id=payload.device_id,
            fcm_token=payload.fcm_token,
            device_type=payload.device_type,
            ip_address=payload.ip_address,
            token=access,
            refresh_token=refresh,
            is_logout=False,
        )
        db.add(login_row)
        db.commit()

    set_session_cache(user.user_id, payload.device_id)
    return build_profile_response(
        db,
        user,
        access_token=access,
        refresh_token=refresh,
        expires_at=exp,
    )


def change_password(db: Session, ctx: AuthContext, *, user_id: str, old_password: str, new_password: str) -> dict[str, str]:
    if user_id != ctx.user_id:
        raise AppException("Forbidden", status_code=403)
    user = get_user_by_id(db, user_id)
    if user is None or not user.password_hash:
        raise AppException("User not found", status_code=404)
    if not verify_password(old_password, user.password_hash):
        raise AppException("Invalid credentials", status_code=401)
    user.password_hash = hash_password(new_password)
    db.commit()
    return {"message": "Password updated"}


def send_otp(_db: Session, payload: SendOtpRequest) -> SendOtpResponse:
    # Spec uses Firebase; for full-spec tests we support a deterministic dev OTP.
    session_info = create_session(payload.phoneNumber)
    return SendOtpResponse(sessionInfo=session_info, success=True, message="OTP sent")


def verify_otp(db: Session, payload: VerifyOtpRequest) -> UserProfileResponse:
    phone = consume_session(payload.sessionInfo, payload.otp)
    if not phone:
        raise AppException("Invalid OTP", status_code=401)

    user = get_user_by_mobile(db, phone)
    if user is None:
        role = get_role_by_type(db, RoleTypeEnum.CUSTOMER)
        if role is None:
            raise AppException("Roles not configured; run database migrations", status_code=500)
        person = Person(full_name="", email="")
        user = User(
            mobile_no=phone,
            password_hash=None,
            city="",
            role_id=role.role_id,
            status=UserStatusEnum.ACTIVE,
            hub_id=None,
            person_id=None,
        )
        db.add(person)
        db.flush()
        user.person_id = person.person_id
        db.add(user)
        db.flush()
        db.commit()
        db.refresh(user)

    person = db.query(Person).filter(Person.person_id == user.person_id).first() if user.person_id else None
    email = person.email if person else ""
    rt = _role_type_value(db, user.role_id)
    access = create_access_token(
        user_id=user.user_id,
        role_id=user.role_id,
        hub_id=user.hub_id,
        email=email,
        mobile_no=user.mobile_no,
        role_type=rt,
    )
    refresh = create_refresh_token(
        user_id=user.user_id,
        role_id=user.role_id,
        hub_id=user.hub_id,
        email=email,
        mobile_no=user.mobile_no,
        role_type=rt,
    )
    exp = _access_expires_at()

    existing = get_login_by_user_and_device(db, user.user_id, payload.device_id)
    if existing:
        existing.token = access
        existing.refresh_token = refresh
        existing.login_at = datetime.now(timezone.utc)
        existing.fcm_token = payload.fcm_token
        existing.device_type = payload.device_type
        existing.ip_address = payload.ip_address
        existing.is_logout = False
        existing.logout_at = None
        update_login(db, existing)
    else:
        login_row = Login(
            user_id=user.user_id,
            device_id=payload.device_id,
            fcm_token=payload.fcm_token,
            device_type=payload.device_type,
            ip_address=payload.ip_address,
            token=access,
            refresh_token=refresh,
            is_logout=False,
        )
        db.add(login_row)
        db.commit()

    set_session_cache(user.user_id, payload.device_id)
    return build_profile_response(
        db,
        user,
        access_token=access,
        refresh_token=refresh,
        expires_at=exp,
    )


def refresh_tokens(db: Session, payload: RefreshTokenRequest) -> RefreshTokenResponse:
    token = payload.refresh_token.strip()
    if not token:
        raise AppException("Refresh token is required", status_code=400)
    body = decode_refresh_token(token)
    row = get_login_by_refresh_token(db, token)
    if row is None:
        raise AppException("Invalid refresh token", status_code=401)
    if row.is_logout:
        raise AppException("Session logged out", status_code=401)
    if str(body.get("sub")) != row.user_id:
        raise AppException("Invalid refresh token", status_code=401)

    user = db.query(User).filter(User.user_id == row.user_id).first()
    if user is None:
        raise AppException("User not found", status_code=401)
    person = db.query(Person).filter(Person.person_id == user.person_id).first() if user.person_id else None
    email = person.email if person else str(body.get("email") or "")

    rt = _role_type_value(db, user.role_id)
    access = create_access_token(
        user_id=user.user_id,
        role_id=user.role_id,
        hub_id=user.hub_id,
        email=email,
        mobile_no=user.mobile_no,
        role_type=rt,
    )
    refresh = create_refresh_token(
        user_id=user.user_id,
        role_id=user.role_id,
        hub_id=user.hub_id,
        email=email,
        mobile_no=user.mobile_no,
        role_type=rt,
    )
    row.token = access
    row.refresh_token = refresh
    row.login_at = datetime.now(timezone.utc)
    row.updated_at = datetime.now(timezone.utc)
    row.is_logout = False
    update_login(db, row)
    return RefreshTokenResponse(access_token=access, refresh_token=refresh)


def is_user_registered(db: Session, payload: IsUserRegisteredRequest) -> bool:
    return get_user_by_mobile(db, payload.mobile_no) is not None


def logout_user(db: Session, payload: LogoutRequest) -> dict[str, str]:
    row = get_login_by_user_and_device(db, payload.user_id, payload.device_id)
    if row is None:
        raise AppException("Session not found", status_code=404)
    row.is_logout = True
    row.logout_at = datetime.now(timezone.utc)
    update_login(db, row)
    delete_session_cache(payload.user_id, payload.device_id)
    return {"message": "Logged out"}
