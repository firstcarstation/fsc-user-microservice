from typing import Optional

from sqlalchemy.orm import Session

from app.models.person_model import Person


def get_person_by_id(db: Session, person_id: str) -> Optional[Person]:
    return db.query(Person).filter(Person.person_id == person_id).first()
