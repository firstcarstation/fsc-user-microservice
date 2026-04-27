from sqlalchemy.orm import Session

from fastapi import APIRouter, Depends

from app.api.internal_deps import require_internal_api_key
from app.core.database.dependency import get_db
from app.crud.query.user_query import get_user_by_id
from app.models.enums import RoleTypeEnum, UserStatusEnum
from app.models.person_model import Person
from app.models.role_model import Role
from app.models.user_model import User
from pydantic import BaseModel, Field


class InternalValidateRequest(BaseModel):
    user_id: str = Field(..., min_length=1)


class InternalValidateResponse(BaseModel):
    valid: bool
    role_type: str | None = None
    user_id: str


class InternalListRecoveryIdsRequest(BaseModel):
    """Role types that should receive dispatch-style job notifications."""

    role_types: list[str] = Field(
        default_factory=lambda: ["agent", "mechanic", "technician"],
        description="Lowercase role_type values as stored on roles.role_type",
    )


class InternalListRecoveryIdsResponse(BaseModel):
    user_ids: list[str]


class InternalProfileRequest(BaseModel):
    user_id: str = Field(..., min_length=1)


class InternalProfileResponse(BaseModel):
    user_id: str
    full_name: str | None = None
    mobile_no: str | None = None


router = APIRouter()


@router.post("/validate", response_model=InternalValidateResponse)
def internal_validate_user(
    payload: InternalValidateRequest,
    db: Session = Depends(get_db),
    _ok: bool = Depends(require_internal_api_key),
) -> InternalValidateResponse:
    del _ok
    user = get_user_by_id(db, payload.user_id)
    if user is None:
        return InternalValidateResponse(valid=False, role_type=None, user_id=payload.user_id)
    role = db.query(Role).filter(Role.role_id == user.role_id).first()
    rt = role.role_type.value if role else None
    return InternalValidateResponse(valid=True, role_type=rt, user_id=str(user.user_id))


@router.post("/list-recovery-user-ids", response_model=InternalListRecoveryIdsResponse)
def internal_list_recovery_user_ids(
    payload: InternalListRecoveryIdsRequest,
    db: Session = Depends(get_db),
    _ok: bool = Depends(require_internal_api_key),
) -> InternalListRecoveryIdsResponse:
    del _ok
    resolved: list[RoleTypeEnum] = []
    for raw in payload.role_types:
        try:
            resolved.append(RoleTypeEnum(raw))
        except ValueError:
            continue
    if not resolved:
        resolved = [RoleTypeEnum.AGENT, RoleTypeEnum.MECHANIC, RoleTypeEnum.TECHNICIAN]

    rows = (
        db.query(User.user_id)
        .join(Role, User.role_id == Role.role_id)
        .filter(Role.role_type.in_(resolved), User.status == UserStatusEnum.ACTIVE)
        .all()
    )
    return InternalListRecoveryIdsResponse(user_ids=[str(r[0]) for r in rows])


@router.post("/profile", response_model=InternalProfileResponse)
def internal_profile(
    payload: InternalProfileRequest,
    db: Session = Depends(get_db),
    _ok: bool = Depends(require_internal_api_key),
) -> InternalProfileResponse:
    del _ok
    user = get_user_by_id(db, payload.user_id)
    if user is None:
        return InternalProfileResponse(user_id=payload.user_id, full_name=None, mobile_no=None)
    person = db.query(Person).filter(Person.person_id == user.person_id).first() if user.person_id else None
    return InternalProfileResponse(
        user_id=str(user.user_id),
        full_name=(person.full_name if person else None),
        mobile_no=(user.mobile_no if user.mobile_no else None),
    )
