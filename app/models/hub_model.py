import uuid
from sqlalchemy import Column, String, Text

from app.core.database.base import Base


class Hub(Base):
    __tablename__ = "hubs"

    hub_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(100), nullable=False)
    city = Column(Text, nullable=True)
