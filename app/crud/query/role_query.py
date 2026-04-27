from typing import Optional

from sqlalchemy.orm import Session

from app.models.enums import RoleTypeEnum
from app.models.role_model import Role


def get_role_by_type(db: Session, role_type: RoleTypeEnum) -> Optional[Role]:
    return db.query(Role).filter(Role.role_type == role_type).first()


def get_role_by_id(db: Session, role_id: str) -> Optional[Role]:
    return db.query(Role).filter(Role.role_id == role_id).first()
