from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user import UserCreate
from app.core.security import get_password_hash

def get_user(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()

def get_user_by_username(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()

def create_user(db: Session, user: UserCreate):
    hashed_password = get_password_hash(user.password)
    db_user = User(username=user.username, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# 认证用户 (在 auth 路由中使用)
def authenticate_user(db: Session, username: str, password: str):
    user = get_user_by_username(db, username)
    if not user:
        return None
    if not user.is_active:
        return None
    if not verify_password(password, user.hashed_password): # 需要从 security 导入 verify_password
        return None
    return user


def get_all_user(db: Session, skip: int, limit: int):
    return db.query(User).order_by(User.id).offset(skip).limit(limit).all()

def deactivate_user(db: Session, user: User):
    user.is_active = False
    db.commit()


# (导入 verify_password)
from app.core.security import verify_password