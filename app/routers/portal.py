from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from typing import Optional

from app.models.database import get_db
from app.crud import website as crud_website
from app.core.security import get_current_user_optional # 使用可选用户依赖
from app.schemas.user import User # 用于类型提示

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/", response_class=HTMLResponse)
async def read_portal(
    request: Request,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional) # 允许未登录
):
    if current_user:
        # 已登录，获取所有网站
        websites = crud_website.get_websites(db)
    else:
        # 未登录，只获取公开网站
        websites = crud_website.get_public_websites(db)

    return templates.TemplateResponse("portal.html", {
        "request": request,
        "websites": websites,
        "current_user": current_user # 传递用户信息到模板
    })