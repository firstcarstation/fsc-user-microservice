import uuid
from sqlalchemy import Column, Float, String, Text
from sqlalchemy.sql import func
from sqlalchemy.types import DateTime

from app.core.database.base import Base


class Address(Base):
    __tablename__ = "addresses"

    address_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    address_line_1 = Column(Text, nullable=False)
    address_line_2 = Column(Text, nullable=True)
    country = Column(Text, nullable=False)
    city = Column(Text, nullable=False)
    zip_code = Column(String(10), nullable=False)
    address_type = Column(Text, nullable=False)
    # Optional geo fields (used as default pickup coordinates / map pin-drop)
    lat = Column(Float, nullable=True)
    lng = Column(Float, nullable=True)
    place_id = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=True, onupdate=func.now())
