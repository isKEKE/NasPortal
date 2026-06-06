from sqlalchemy.orm import Session
from app.models.tag import Tag
from app.schemas.tag import TagCreate


def get_tag(db: Session, tag_id: int):
    return db.query(Tag).filter(Tag.id == tag_id).first()


def get_tags_by_owner(db: Session, owner_id: int, skip: int = 0, limit: int = 100):
    return (
        db.query(Tag)
        .filter(Tag.owner_id == owner_id)
        .offset(skip)
        .limit(limit)
        .all()
    )


def create_tag(db: Session, tag: TagCreate):
    db_tag = Tag(**tag.model_dump(mode="json"))
    db.add(db_tag)
    db.commit()
    db.refresh(db_tag)
    return db_tag


def update_tag(db: Session, tag_id: int, name: str):
    db_tag = db.query(Tag).filter(Tag.id == tag_id).first()
    if db_tag:
        db_tag.name = name
        db.commit()
        db.refresh(db_tag)
    return db_tag


def delete_tag(db: Session, tag_id: int):
    db_tag = db.query(Tag).filter(Tag.id == tag_id).first()
    if db_tag:
        db.delete(db_tag)
        db.commit()
    return db_tag