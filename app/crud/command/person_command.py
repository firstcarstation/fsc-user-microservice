from sqlalchemy.orm import Session

from app.models.person_model import Person


def save_person(db: Session, person: Person) -> Person:
    db.add(person)
    db.commit()
    db.refresh(person)
    return person
