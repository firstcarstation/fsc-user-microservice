import uuid
from sqlalchemy import Column, Enum as SAEnum, ForeignKey, String, Text
from sqlalchemy.sql import func
from sqlalchemy.types import DateTime

from app.core.database.base import Base
from app.models.enums import UserStatusEnum


class User(Base):
    __tablename__ = "users"

    user_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    person_id = Column(String(36), ForeignKey("persons.person_id", ondelete="SET NULL"), nullable=True)
    mobile_no = Column(String(15), unique=True, nullable=False)
    role_id = Column(String(36), ForeignKey("roles.role_id", ondelete="RESTRICT"), nullable=False)
    city = Column(Text, nullable=False)
    status = Column(SAEnum(UserStatusEnum, name="user_status_enum"), nullable=False, default=UserStatusEnum.ACTIVE)
    hub_id = Column(String(36), ForeignKey("hubs.hub_id", ondelete="SET NULL"), nullable=True)
    password_hash = Column(String(255), nullable=True)  # added per requirement
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=True, onupdate=func.now())
