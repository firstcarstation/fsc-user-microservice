import uuid
from sqlalchemy import Column, Enum as SAEnum, String, Text
from sqlalchemy.sql import func
from sqlalchemy.types import DateTime

from app.core.database.base import Base
from app.models.enums import RoleTypeEnum


class Role(Base):
    __tablename__ = "roles"

    role_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    role_type = Column(
        SAEnum(
            RoleTypeEnum,
            name="role_type_enum",
            values_callable=lambda e: [m.value for m in e],  # store lowercase values in DB enum
        ),
        nullable=False,
    )
    company_name = Column(Text, nullable=True)
    company_tin_number = Column(Text, nullable=True)
    company_trade_license_number = Column(Text, nullable=True)
    company_landline_number = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=True, onupdate=func.now())
