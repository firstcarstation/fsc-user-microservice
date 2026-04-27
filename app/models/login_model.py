import uuid
from sqlalchemy import Column, Boolean, ForeignKey, String, Text
from sqlalchemy.sql import func
from sqlalchemy.types import DateTime

from app.core.database.base import Base


class Login(Base):
    __tablename__ = "logins"

    login_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(128), ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    login_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    refresh_token = Column(Text, nullable=True)
    firebase_uid = Column(String(128), nullable=True)
    token = Column(Text, nullable=True)
    device_id = Column(Text, nullable=False)
    device_type = Column(String(50), nullable=True)
    fcm_token = Column(Text, nullable=False)
    ip_address = Column(String(50), nullable=True)
    is_logout = Column(Boolean, nullable=True)
    logout_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=True, onupdate=func.now())
