from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer # 或使用 Cookie
from jose import JWTError, jwt # 假设使用 JWT, Session 方式不同
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from typing import Optional

from app.models.database import get_db
from app.crud import user as crud_user
from app.schemas.user import User

# !! 强烈建议将密钥存储在环境变量中 !!
SECRET_KEY = "YOUR_VERY_SECRET_KEY" # 必须更改并保密
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token") # 如果 API 返回 Token
# 这里我们假设 token 存在 cookie 中, 需要自定义依赖

def verify_password(plain_password, hashed_password):
    print(plain_password, hashed_password)
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# --- 依赖项: 获取当前用户 ---
# 这个实现假设 Token 存在于名为 'access_token' 的 Cookie 中
async def get_current_user(request: Request, db: Session = Depends(get_db)) -> User:
    token = request.cookies.get("access_token")
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"}, # 或者重定向到登录页
    )
    if token is None:
         # 可以重定向到登录页, 而不是抛出异常
         # from fastapi.responses import RedirectResponse
         # return RedirectResponse(url='/auth/login', status_code=status.HTTP_302_FOUND)
         raise credentials_exception

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = crud_user.get_user_by_username(db, username=username)
    if user is None:
        raise credentials_exception
    return user

# 可选用户: 如果未登录则返回 None
async def get_current_user_optional(request: Request, db: Session = Depends(get_db)) -> Optional[User]:
    try:
        return await get_current_user(request, db)
    except HTTPException as e:
        # 只捕获未授权异常, 其他异常应继续抛出
        if e.status_code == status.HTTP_401_UNAUTHORIZED:
            return None
        raise e