from typing import Optional
from sqlalchemy.orm import Session
from app.models.user_model import User


def get_user_by_id(db: Session, user_id: str) -> Optional[User]:
    return db.query(User).filter(User.user_id == user_id).first()


def get_user_by_mobile(db: Session, mobile_no: str) -> Optional[User]:
    return db.query(User).filter(User.mobile_no == mobile_no).first()
