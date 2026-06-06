from sqlalchemy.orm import Session

from app.models.user import User
from app.schemas.user import UserCreate


def get_user(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()


def get_user_by_username(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()


def create_user(db: Session, user: UserCreate):
    from app.core.security import get_password_hash

    hashed_password = get_password_hash(user.password)
    db_user = User(
        username=user.username,
        hashed_password=hashed_password,
        is_superuser=user.is_superuser,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def ensure_user(db: Session, user: UserCreate):
    from app.core.security import get_password_hash

    db_user = get_user_by_username(db, user.username)
    if db_user is None:
        return create_user(db, user)

    db_user.hashed_password = get_password_hash(user.password)
    db_user.is_superuser = user.is_superuser
    db_user.is_active = True
    db.commit()
    db.refresh(db_user)
    return db_user


def authenticate_user(db: Session, username: str, password: str):
    from app.core.security import verify_password

    user = get_user_by_username(db, username)
    if not user or not user.is_active:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


def get_all_user(db: Session, skip: int, limit: int):
    return db.query(User).order_by(User.id).offset(skip).limit(limit).all()


def deactivate_user(db: Session, user: User):
    user.is_active = False
    db.commit()
