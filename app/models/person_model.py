import uuid
from datetime import date
from sqlalchemy import Column, Date, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.sql import func
from sqlalchemy.types import DateTime

from app.core.database.base import Base


class Person(Base):
    __tablename__ = "persons"

    person_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    full_name = Column(Text, nullable=False)
    email = Column(Text, nullable=False)
    alternate_mobile_no = Column(String(15), nullable=True)
    permanent_address_id = Column(String(36), ForeignKey("addresses.address_id", ondelete="SET NULL"), nullable=True)
    current_address_id = Column(String(36), ForeignKey("addresses.address_id", ondelete="SET NULL"), nullable=True)
    # Extra labelled addresses (home/office/etc.) stored as JSON list of address dicts.
    saved_addresses = Column(JSON, nullable=True)
    # Index in saved_addresses list that is treated as "default" (0-based).
    saved_addresses_default_index = Column(Integer, nullable=True)
    dob = Column(Date, nullable=True)
    image_path = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=True, onupdate=func.now())
