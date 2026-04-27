from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps import AuthContext, get_current_user
from app.core.database.dependency import get_db
from app.core.exceptions import AppException
from app.schemas.auth_schema import (
    ChangePasswordRequest,
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
from app.services import auth_service

router = APIRouter()


@router.post("/send-otp", response_model=SendOtpResponse)
def send_otp(payload: SendOtpRequest, db: Session = Depends(get_db)) -> SendOtpResponse:
    return auth_service.send_otp(db, payload)


@router.post("/verify-otp", response_model=UserProfileResponse)
def verify_otp(payload: VerifyOtpRequest, db: Session = Depends(get_db)) -> UserProfileResponse:
    return auth_service.verify_otp(db, payload)


@router.post("/refresh", response_model=RefreshTokenResponse)
def refresh_token(payload: RefreshTokenRequest, db: Session = Depends(get_db)) -> RefreshTokenResponse:
    return auth_service.refresh_tokens(db=db, payload=payload)


@router.post("/register", response_model=UserProfileResponse, status_code=status.HTTP_201_CREATED)
def register(payload: RegisterRequest, db: Session = Depends(get_db)) -> UserProfileResponse:
    return auth_service.register_user(db=db, payload=payload)


@router.post("/admin/register-staff")
def admin_register_staff(
    payload: RegisterRequest,
    db: Session = Depends(get_db),
    ctx: AuthContext = Depends(get_current_user),
) -> dict[str, str]:
    return auth_service.admin_create_staff(db=db, admin_user_id=ctx.user_id, payload=payload)


@router.post("/login", response_model=UserProfileResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> UserProfileResponse:
    return auth_service.login_user(db=db, payload=payload)


@router.post("/is_user_registered")
def is_user_registered(payload: IsUserRegisteredRequest, db: Session = Depends(get_db)) -> dict[str, bool]:
    return {"registered": auth_service.is_user_registered(db=db, payload=payload)}


@router.post("/logout")
def logout(
    payload: LogoutRequest,
    db: Session = Depends(get_db),
    ctx: AuthContext = Depends(get_current_user),
) -> dict[str, str]:
    if payload.user_id != ctx.user_id:
        raise AppException("Forbidden", status_code=403)
    return auth_service.logout_user(db=db, payload=payload)


@router.post("/change-password")
def change_password(
    payload: ChangePasswordRequest,
    db: Session = Depends(get_db),
    ctx: AuthContext = Depends(get_current_user),
) -> dict[str, str]:
    return auth_service.change_password(
        db=db,
        ctx=ctx,
        user_id=payload.user_id,
        old_password=payload.old_password,
        new_password=payload.new_password,
    )
