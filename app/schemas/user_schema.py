from datetime import datetime
from typing import Optional
from pydantic import BaseModel


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

    class Config:
        from_attributes = True
