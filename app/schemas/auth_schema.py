from typing import Optional

from pydantic import BaseModel, Field


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class RefreshTokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RegisterRequest(BaseModel):
    mobile_no: str = Field(..., max_length=15)
    password: str = Field(..., min_length=6)
    full_name: str
    email: str
    city: str
    role_type: str = "customer"
    device_id: str
    fcm_token: str = Field(..., min_length=1)
    device_type: Optional[str] = Field(None, max_length=50)
    hub_id: Optional[str] = None
    ip_address: Optional[str] = Field(None, max_length=50)


class LoginRequest(BaseModel):
    mobile_no: str = Field(..., max_length=15)
    password: str = Field(..., min_length=1)
    device_id: str
    fcm_token: str = Field(..., min_length=1)
    device_type: Optional[str] = Field(None, max_length=50)
    ip_address: Optional[str] = Field(None, max_length=50)


class SendOtpRequest(BaseModel):
    phoneNumber: str = Field(..., max_length=15)
    recaptchaToken: Optional[str] = None


class SendOtpResponse(BaseModel):
    sessionInfo: str
    success: bool = True
    message: str = "OTP sent"


class VerifyOtpRequest(BaseModel):
    sessionInfo: str = Field(..., min_length=1)
    otp: str = Field(..., min_length=1)
    device_id: str
    fcm_token: str = Field(..., min_length=1)
    device_type: Optional[str] = Field(None, max_length=50)
    ip_address: Optional[str] = Field(None, max_length=50)


class IsUserRegisteredRequest(BaseModel):
    mobile_no: str = Field(..., max_length=15)


class LogoutRequest(BaseModel):
    user_id: str
    device_id: str


class ChangePasswordRequest(BaseModel):
    user_id: str
    old_password: str = Field(..., min_length=6)
    new_password: str = Field(..., min_length=6)
