from fastapi import APIRouter, Depends, HTTPException, status, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from datetime import timedelta

from app.models.database import get_db
from app.crud import user as crud_user
from app.core.security import create_access_token, get_password_hash, verify_password, ACCESS_TOKEN_EXPIRE_MINUTES

router = APIRouter(
    prefix="/auth",
    tags=["authentication"]
)

templates = Jinja2Templates(directory="app/templates")


@router.get("/login", response_class=HTMLResponse)
async def login_form(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@router.post("/login") # HTMLResponse 用于渲染错误, RedirectResponse 用于成功
async def login_for_access_token(
    request: Request,
    db: Session = Depends(get_db),
    username: str = Form(...),
    password: str = Form(...)
):
    user = crud_user.authenticate_user(db, username, password)
    if not user:
        # 登录失败，重新渲染登录页并显示错误
        return templates.TemplateResponse("login.html", {
            "request": request,
            "error": "用户名或密码错误"
        }, status_code=status.HTTP_401_UNAUTHORIZED)

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )

    # 登录成功，重定向到首页，并在 Cookie 中设置 Token
    response = RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
    response.set_cookie(key="access_token", value=access_token, httponly=True, max_age=int(access_token_expires.total_seconds()), samesite='Lax') # httponly 很重要!
    return response


@router.get("/logout")
async def logout(request: Request):
    # 重定向到首页并删除 Cookie
    response = RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
    response.delete_cookie("access_token")
    return response


# --- 注册示例 (非常基础) ---
# @router.get("/register", response_class=HTMLResponse)
# async def register_form(request: Request):
#     # return templates.TemplateResponse("register.html", {"request": request}) # 需要创建 register.html
#     raise HTTPException(status_code=501, detail="Registration form not implemented")

# @router.post("/register")
# async def register_user(
#     request: Request,
#     db: Session = Depends(get_db),
#     username: str = Form(...),
#     password: str = Form(...)
# ):
#     existing_user = crud_user.get_user_by_username(db, username)
#     if existing_user:
#         # return templates.TemplateResponse("register.html", {"request": request, "error": "Username already exists"}, status_code=400)
#         raise HTTPException(status_code=400, detail="Username already registered")
#     user_in = UserCreate(username=username, password=password) # 需要 UserCreate schema
#     crud_user.create_user(db=db, user=user_in)
#     # 可以自动登录或重定向到登录页
#     return RedirectResponse(url="/auth/login", status_code=status.HTTP_303_SEE_OTHER)