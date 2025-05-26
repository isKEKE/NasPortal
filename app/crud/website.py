from sqlalchemy.orm import Session, joinedload
from app.models.website import Website
from app.models.user import User
from app.schemas.website import WebsiteCreate


def get_website_by_user(db: Session, user_id:int, website_id: int):
    return db.query(Website).options(joinedload(Website.owner)).filter(
        (Website.owner_id==user_id) & (Website.id == website_id)
    ).first()


def get_websites_by_user(db: Session, user_id: int, skip: int = 0, limit: int = 100):
    return (
        db.query(Website)
        .options(joinedload(Website.owner))
        .filter(Website.owner_id == user_id)
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_websites(db: Session, skip: int = 0, limit: int = 100):
    return (
        db.query(Website)
        .options(joinedload(Website.owner))
        .order_by(Website.id)
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_public_websites(db: Session, skip: int = 0, limit: int = 100):
    return (
        db.query(Website)
        .join(Website.owner)
        .options(joinedload(Website.owner))
        .filter((Website.is_public == True) & (User.is_superuser == True))
        .offset(skip)
        .limit(limit)
        .all()
    )


def create_website(db: Session, website: WebsiteCreate):
    db_website = Website(**website.model_dump(mode="json"))
    db.add(db_website)
    db.commit()
    db.refresh(db_website)
    return db_website


def update_website(db: Session, db_website: Website, website: WebsiteCreate):
    update_data = website.model_dump(exclude_unset=True, mode="json")
    for key, value in update_data.items():
        setattr(db_website, key, value)
    db.commit()
    db.refresh(db_website)
    return db_website


def delete_website(db: Session, db_website: Website):
    db.delete(db_website)
    db.commit()
    return db_website
