from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class AddressBlock(BaseModel):
    address_line_1: str
    address_line_2: Optional[str] = None
    country: str
    city: str
    zip_code: str = Field(..., max_length=10)
    address_type: str = "current"
    lat: Optional[float] = None
    lng: Optional[float] = None
    place_id: Optional[str] = None


class SavedAddressBlock(AddressBlock):
    """Additional saved locations (e.g. office, home 2) stored as JSON on the person."""

    label: Optional[str] = Field(None, max_length=64)
    address_type: str = "saved"


class AddressOut(BaseModel):
    address_id: str
    address_line_1: str
    address_line_2: Optional[str] = None
    country: str
    city: str
    zip_code: str
    address_type: str
    lat: Optional[float] = None
    lng: Optional[float] = None
    place_id: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class RoleInfo(BaseModel):
    role_id: str
    role_type: str
    company_name: Optional[str] = None
    company_tin_number: Optional[str] = None
    company_trade_license_number: Optional[str] = None
    company_landline_number: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class UserProfileResponse(BaseModel):
    user_id: str
    mobile_no: str
    city: str
    status: str
    recovery_on_duty: bool = False
    hub_id: Optional[str] = None
    person_id: Optional[str] = None
    full_name: Optional[str] = None
    email: Optional[str] = None
    alternate_mobile_no: Optional[str] = None
    dob: Optional[date] = None
    image_path: Optional[str] = None
    role: RoleInfo
    permanent_address: Optional[AddressOut] = None
    current_address: Optional[AddressOut] = None
    saved_addresses: list[SavedAddressBlock] = Field(default_factory=list)
    saved_addresses_default_index: Optional[int] = None
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    token_type: Optional[str] = "bearer"
    expires_at: Optional[datetime] = None


class ViewProfileRequest(BaseModel):
    user_id: str


class UpdateProfileRequest(BaseModel):
    user_id: str
    full_name: Optional[str] = None
    email: Optional[str] = None
    city: Optional[str] = None
    status: Optional[str] = None
    recovery_on_duty: Optional[bool] = None
    alternate_mobile_no: Optional[str] = Field(None, max_length=15)
    dob: Optional[date] = None
    hub_id: Optional[str] = None
    permanent_address: Optional[AddressBlock] = None
    current_address: Optional[AddressBlock] = None
    saved_addresses: Optional[list[SavedAddressBlock]] = None
    saved_addresses_default_index: Optional[int] = None
    company_name: Optional[str] = None
    company_tin_number: Optional[str] = None
    company_trade_license_number: Optional[str] = None
    company_landline_number: Optional[str] = None


class UpdateProfileResponse(BaseModel):
    message: str = "Updated"


class UpdateUserImageRequest(BaseModel):
    user_id: str
    image_url: str


class UpdateUserImageResponse(BaseModel):
    message: str = "Updated"


class UpdateFcmTokenRequest(BaseModel):
    device_id: str
    fcm_token: str = Field(..., min_length=1)


class UpdateFcmTokenResponse(BaseModel):
    message: str = "Updated"


class UploadPhotoResponse(BaseModel):
    url: str


# Legacy minimal schemas (internal)
class UserBase(BaseModel):
    mobile_no: str
    role_id: str
    city: str
    hub_id: Optional[str] = None
    person_id: Optional[str] = None


class UserCreate(UserBase):
    password: Optional[str] = None


class UserRead(UserBase):
    user_id: str
    status: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
