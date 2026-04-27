from typing import Optional

from sqlalchemy.orm import Session

from app.models.login_model import Login


def get_login_by_refresh_token(db: Session, refresh_token: str) -> Optional[Login]:
    return db.query(Login).filter(Login.refresh_token == refresh_token).first()


def get_login_by_user_and_device(db: Session, user_id: str, device_id: str) -> Optional[Login]:
    return (
        db.query(Login)
        .filter(Login.user_id == user_id, Login.device_id == device_id)
        .first()
    )
