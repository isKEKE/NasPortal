from sqlalchemy.orm import Session
from app.models.website import Website
from app.schemas.website import WebsiteCreate

def get_website(db: Session, website_id: int):
    return db.query(Website).filter(Website.id == website_id).first()

def get_websites(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Website).offset(skip).limit(limit).all()

def get_public_websites(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Website).filter(Website.is_public == True).offset(skip).limit(limit).all()

def create_website(db: Session, website: WebsiteCreate):
    db_website = Website(**website.dict())
    db.add(db_website)
    db.commit()
    db.refresh(db_website)
    return db_website

def update_website(db: Session, website_id: int, website_data: WebsiteCreate):
    db_website = get_website(db, website_id)
    if db_website:
        update_data = website_data.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_website, key, value)
        db.commit()
        db.refresh(db_website)
    return db_website

def delete_website(db: Session, website_id: int):
    db_website = get_website(db, website_id)
    if db_website:
        db.delete(db_website)
        db.commit()
    return db_website