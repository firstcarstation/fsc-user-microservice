from sqlalchemy.orm import Session

from app.models.address_model import Address


def save_address(db: Session, address: Address) -> Address:
    db.add(address)
    db.commit()
    db.refresh(address)
    return address
