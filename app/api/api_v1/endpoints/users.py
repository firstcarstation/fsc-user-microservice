from fastapi import APIRouter, Depends, File, UploadFile
from sqlalchemy.orm import Session

from app.api.deps import AuthContext, get_current_user
from app.core.database.dependency import get_db
from app.core.exceptions import AppException
from app.models.enums import RoleTypeEnum, UserStatusEnum
from app.models.role_model import Role
from app.models.user_model import User
from app.models.person_model import Person
from app.schemas.admin_schema import AdminBulkProfilesRequest, AdminBulkProfilesResponse
from app.schemas.user_schema import (
    UpdateFcmTokenRequest,
    UpdateFcmTokenResponse,
    UpdateProfileRequest,
    UpdateProfileResponse,
    UpdateUserImageRequest,
    UpdateUserImageResponse,
    UploadPhotoResponse,
    UserProfileResponse,
    ViewProfileRequest,
)
from app.services import user_service

router = APIRouter()

def _require_staff(ctx: AuthContext, db: Session) -> None:
    if not ctx.role_id:
        raise AppException("Forbidden", status_code=403)
    role = db.query(Role).filter(Role.role_id == ctx.role_id).first()
    rt = role.role_type if role else None
    if rt not in (RoleTypeEnum.ADMIN, RoleTypeEnum.HUB_MANAGER):
        raise AppException("Forbidden", status_code=403)


@router.put("/update_profile", response_model=UpdateProfileResponse)
def update_profile(
    payload: UpdateProfileRequest,
    db: Session = Depends(get_db),
    ctx: AuthContext = Depends(get_current_user),
) -> UpdateProfileResponse:
    return user_service.update_profile(db=db, payload=payload, ctx=ctx)


@router.post("/profile", response_model=UserProfileResponse)
def view_profile(
    payload: ViewProfileRequest,
    db: Session = Depends(get_db),
    ctx: AuthContext = Depends(get_current_user),
) -> UserProfileResponse:
    return user_service.view_profile(db=db, payload=payload, ctx=ctx)


@router.post("/upload-photo", response_model=UploadPhotoResponse)
def upload_photo(
    db: Session = Depends(get_db),
    ctx: AuthContext = Depends(get_current_user),
    file: UploadFile = File(...),
) -> UploadPhotoResponse:
    raw = file.file.read()
    return user_service.upload_profile_photo(
        db=db, user_id=ctx.user_id, file_bytes=raw, filename=file.filename or "photo", ctx=ctx
    )


@router.post("/update-user-image", response_model=UpdateUserImageResponse)
def update_user_image(
    payload: UpdateUserImageRequest,
    db: Session = Depends(get_db),
    ctx: AuthContext = Depends(get_current_user),
) -> UpdateUserImageResponse:
    return user_service.update_user_image(db=db, payload=payload, ctx=ctx)


@router.post("/update-fcm-token", response_model=UpdateFcmTokenResponse)
def update_fcm_token(
    payload: UpdateFcmTokenRequest,
    db: Session = Depends(get_db),
    ctx: AuthContext = Depends(get_current_user),
) -> UpdateFcmTokenResponse:
    return user_service.update_fcm_token(db=db, payload=payload, ctx=ctx)


@router.post("/admin/search")
def admin_user_search(
    payload: dict,
    db: Session = Depends(get_db),
    ctx: AuthContext = Depends(get_current_user),
) -> dict:
    """Search users for admin ticket creation.

    Input: {"query": "name/mobile/email"}
    Output: {"users": [{"user_id","full_name","mobile_no","email","city"}]}
    """
    _require_staff(ctx, db)
    q = str(payload.get("query") or "").strip()
    if len(q) < 2:
        return {"users": []}
    like = f"%{q.lower()}%"
    rows = (
        db.query(User, Person)
        .outerjoin(Person, User.person_id == Person.person_id)
        .filter(
            (User.mobile_no.ilike(like))
            | (Person.full_name.ilike(like))
            | (Person.email.ilike(like))
        )
        .order_by(User.created_at.desc())
        .limit(20)
        .all()
    )
    out = []
    for u, p in rows:
        out.append(
            {
                "user_id": str(u.user_id),
                "mobile_no": u.mobile_no,
                "city": u.city,
                "full_name": (p.full_name if p else None),
                "email": (p.email if p else None),
            }
        )
    return {"users": out}


@router.post("/admin/bulk-profiles", response_model=AdminBulkProfilesResponse)
def admin_bulk_profiles(
    payload: AdminBulkProfilesRequest,
    db: Session = Depends(get_db),
    ctx: AuthContext = Depends(get_current_user),
) -> AdminBulkProfilesResponse:
    _require_staff(ctx, db)
    ids = [str(x).strip() for x in (payload.user_ids or []) if str(x).strip()]
    if not ids:
        return AdminBulkProfilesResponse(users=[])
    rows = (
        db.query(User, Person)
        .outerjoin(Person, User.person_id == Person.person_id)
        .filter(User.user_id.in_(ids))
        .all()
    )
    out = []
    for u, p in rows:
        out.append(
            {
                "user_id": str(u.user_id),
                "mobile_no": u.mobile_no,
                "city": u.city,
                "full_name": (p.full_name if p else None),
                "email": (p.email if p else None),
            }
        )
    return AdminBulkProfilesResponse(users=out)


@router.get("/admin/recovery-roster")
def admin_recovery_roster(
    db: Session = Depends(get_db),
    ctx: AuthContext = Depends(get_current_user),
) -> dict:
    """List recovery drivers for admin delivery scheduling."""
    _require_staff(ctx, db)
    agent_role = db.query(Role).filter(Role.role_type == RoleTypeEnum.AGENT).first()
    if not agent_role:
        return {"drivers": []}
    rows = (
        db.query(User, Person)
        .outerjoin(Person, User.person_id == Person.person_id)
        .filter(User.role_id == agent_role.role_id, User.status == UserStatusEnum.ACTIVE)
        .order_by(User.updated_at.desc())
        .limit(200)
        .all()
    )
    out = []
    for u, p in rows:
        out.append(
            {
                "user_id": str(u.user_id),
                "full_name": (p.full_name if p else None),
                "mobile_no": u.mobile_no,
                "city": u.city,
                "recovery_on_duty": bool(getattr(u, "recovery_on_duty", False)),
            }
        )
    return {"drivers": out}
