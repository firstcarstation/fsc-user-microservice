from sqlalchemy.orm import Session
from app.models.user_model import User


def create_user(db: Session, user: User) -> User:
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
