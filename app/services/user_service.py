from __future__ import annotations

from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from app.core.exceptions import AppException
from app.core.security import AuthContext
from app.core.storage import save_profile_image
from app.crud.command.address_command import save_address
from app.crud.command.login_command import update_login
from app.crud.command.person_command import save_person
from app.crud.query.address_query import get_address_by_id
from app.crud.query.login_query import get_login_by_user_and_device
from app.crud.query.person_query import get_person_by_id
from app.crud.query.role_query import get_role_by_id
from app.crud.query.user_query import get_user_by_id
from app.models.address_model import Address
from app.models.enums import RoleTypeEnum, UserStatusEnum
from app.models.person_model import Person
from app.models.role_model import Role
from app.models.user_model import User
from app.schemas.user_schema import (
    AddressBlock,
    AddressOut,
    RoleInfo,
    SavedAddressBlock,
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


def _enum_str(v: object) -> str:
    if hasattr(v, "value"):
        return str(v.value)
    return str(v)


def _address_out(addr: Address) -> AddressOut:
    return AddressOut(
        address_id=addr.address_id,
        address_line_1=addr.address_line_1,
        address_line_2=addr.address_line_2,
        country=addr.country,
        city=addr.city,
        zip_code=addr.zip_code,
        address_type=addr.address_type,
        lat=getattr(addr, "lat", None),
        lng=getattr(addr, "lng", None),
        place_id=getattr(addr, "place_id", None),
    )


def _role_info(role: Role) -> RoleInfo:
    return RoleInfo(
        role_id=role.role_id,
        role_type=_enum_str(role.role_type),
        company_name=role.company_name,
        company_tin_number=role.company_tin_number,
        company_trade_license_number=getattr(role, "company_trade_license_number", None),
        company_landline_number=getattr(role, "company_landline_number", None),
    )


def build_profile_response(
    db: Session,
    user: User,
    *,
    access_token: str | None = None,
    refresh_token: str | None = None,
    expires_at: datetime | None = None,
) -> UserProfileResponse:
    role = get_role_by_id(db, user.role_id)
    if role is None:
        raise AppException("Role not found", status_code=500)
    person = get_person_by_id(db, user.person_id) if user.person_id else None
    perm = (
        get_address_by_id(db, person.permanent_address_id)
        if person and person.permanent_address_id
        else None
    )
    curr = (
        get_address_by_id(db, person.current_address_id) if person and person.current_address_id else None
    )
    extras: list[SavedAddressBlock] = []
    if person and getattr(person, "saved_addresses", None):
        raw = person.saved_addresses
        if isinstance(raw, list):
            for item in raw:
                if isinstance(item, dict):
                    try:
                        extras.append(SavedAddressBlock.model_validate(item))
                    except Exception:
                        continue
    default_idx = None
    if person is not None:
        default_idx = getattr(person, "saved_addresses_default_index", None)
    return UserProfileResponse(
        user_id=user.user_id,
        mobile_no=user.mobile_no,
        city=user.city,
        status=_enum_str(user.status),
        recovery_on_duty=bool(getattr(user, "recovery_on_duty", False)),
        hub_id=user.hub_id,
        person_id=user.person_id,
        full_name=person.full_name if person else None,
        email=person.email if person else None,
        alternate_mobile_no=person.alternate_mobile_no if person else None,
        dob=person.dob if person else None,
        image_path=person.image_path if person else None,
        role=_role_info(role),
        permanent_address=_address_out(perm) if perm else None,
        current_address=_address_out(curr) if curr else None,
        saved_addresses=extras,
        saved_addresses_default_index=default_idx,
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer" if access_token else None,
        expires_at=expires_at,
    )


def view_profile(db: Session, payload: ViewProfileRequest, ctx: AuthContext) -> UserProfileResponse:
    if payload.user_id != ctx.user_id:
        raise AppException("Forbidden", status_code=403)
    user = get_user_by_id(db, payload.user_id)
    if user is None:
        raise AppException("User not found", status_code=404)
    return build_profile_response(db, user)


def _upsert_address(db: Session, block: AddressBlock) -> Address:
    addr = Address(
        address_line_1=block.address_line_1,
        address_line_2=block.address_line_2,
        country=block.country,
        city=block.city,
        zip_code=block.zip_code,
        address_type=block.address_type,
        lat=block.lat,
        lng=block.lng,
        place_id=block.place_id,
    )
    return save_address(db, addr)


def update_profile(db: Session, payload: UpdateProfileRequest, ctx: AuthContext) -> UpdateProfileResponse:
    if payload.user_id != ctx.user_id:
        raise AppException("Forbidden", status_code=403)
    user = get_user_by_id(db, payload.user_id)
    if user is None:
        raise AppException("User not found", status_code=404)
    person = get_person_by_id(db, user.person_id) if user.person_id else None
    if person is None:
        raise AppException("Person not found", status_code=404)

    if payload.full_name is not None:
        person.full_name = payload.full_name
    if payload.email is not None:
        person.email = payload.email
    if payload.alternate_mobile_no is not None:
        person.alternate_mobile_no = payload.alternate_mobile_no
    if payload.dob is not None:
        person.dob = payload.dob
    if payload.city is not None:
        user.city = payload.city
    if payload.hub_id is not None:
        user.hub_id = payload.hub_id
    if payload.status is not None:
        try:
            user.status = UserStatusEnum(payload.status)
        except ValueError as e:
            raise AppException("Invalid status", status_code=400) from e

    if payload.recovery_on_duty is not None:
        user.recovery_on_duty = payload.recovery_on_duty

    if payload.permanent_address is not None:
        addr = _upsert_address(db, payload.permanent_address)
        person.permanent_address_id = addr.address_id
    if payload.current_address is not None:
        addr = _upsert_address(db, payload.current_address)
        person.current_address_id = addr.address_id

    if payload.saved_addresses is not None:
        person.saved_addresses = [b.model_dump(exclude_none=True) for b in payload.saved_addresses]

    if payload.saved_addresses_default_index is not None:
        # Persist customer’s "default" saved address selection server-side.
        idx = payload.saved_addresses_default_index
        if idx < 0:
            raise AppException("Invalid saved_addresses_default_index", status_code=400)
        if payload.saved_addresses is not None and idx >= len(payload.saved_addresses):
            raise AppException("Invalid saved_addresses_default_index", status_code=400)
        person.saved_addresses_default_index = idx

    if (
        payload.company_name is not None
        or payload.company_tin_number is not None
        or payload.company_trade_license_number is not None
        or payload.company_landline_number is not None
    ):
        current_role = get_role_by_id(db, user.role_id)
        if current_role is None:
            raise AppException("Role not found", status_code=500)
        new_role = Role(
            role_type=current_role.role_type,
            company_name=payload.company_name if payload.company_name is not None else current_role.company_name,
            company_tin_number=(
                payload.company_tin_number
                if payload.company_tin_number is not None
                else current_role.company_tin_number
            ),
            company_trade_license_number=(
                payload.company_trade_license_number
                if payload.company_trade_license_number is not None
                else getattr(current_role, "company_trade_license_number", None)
            ),
            company_landline_number=(
                payload.company_landline_number
                if payload.company_landline_number is not None
                else getattr(current_role, "company_landline_number", None)
            ),
        )
        db.add(new_role)
        db.flush()
        user.role_id = new_role.role_id

    db.add(person)
    db.add(user)
    db.commit()
    db.refresh(person)
    db.refresh(user)
    return UpdateProfileResponse()


def upload_profile_photo(db: Session, user_id: str, file_bytes: bytes, filename: str, ctx: AuthContext) -> UploadPhotoResponse:
    if user_id != ctx.user_id:
        raise AppException("Forbidden", status_code=403)
    user = get_user_by_id(db, user_id)
    if user is None or not user.person_id:
        raise AppException("User not found", status_code=404)
    url = save_profile_image(user_id, file_bytes, filename)
    return UploadPhotoResponse(url=url)


def update_user_image(db: Session, payload: UpdateUserImageRequest, ctx: AuthContext) -> UpdateUserImageResponse:
    if payload.user_id != ctx.user_id:
        raise AppException("Forbidden", status_code=403)
    user = get_user_by_id(db, payload.user_id)
    if user is None or not user.person_id:
        raise AppException("User not found", status_code=404)
    person = get_person_by_id(db, user.person_id)
    if person is None:
        raise AppException("Person not found", status_code=404)
    person.image_path = payload.image_url
    save_person(db, person)
    return UpdateUserImageResponse()


def update_fcm_token(db: Session, payload: UpdateFcmTokenRequest, ctx: AuthContext) -> UpdateFcmTokenResponse:
    row = get_login_by_user_and_device(db, ctx.user_id, payload.device_id)
    if row is None:
        raise AppException("Session not found", status_code=404)
    row.fcm_token = payload.fcm_token
    update_login(db, row)
    return UpdateFcmTokenResponse()
