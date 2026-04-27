from sqlalchemy.orm import Session

from app.models.login_model import Login


def save_login(db: Session, login: Login) -> Login:
    db.add(login)
    db.commit()
    db.refresh(login)
    return login


def update_login(db: Session, login: Login) -> Login:
    db.add(login)
    db.commit()
    db.refresh(login)
    return login
