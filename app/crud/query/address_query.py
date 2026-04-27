from typing import Optional

from sqlalchemy.orm import Session

from app.models.address_model import Address


def get_address_by_id(db: Session, address_id: str) -> Optional[Address]:
    return db.query(Address).filter(Address.address_id == address_id).first()
