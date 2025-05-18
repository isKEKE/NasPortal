from fastapi import APIRouter, Depends, Request, Form, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from typing import Annotated, Optional # 使用 Annotated for Form Data in newer FastAPI

from app.models.database import get_db
from app.crud import website as crud_website
from app.schemas.website import WebsiteCreate # 用于创建和可能的更新验证
from app.schemas.user import User # 用于类型提示
from app.core.security import get_current_user # 强制登录

router = APIRouter(
    prefix="/admin",
    tags=["admin"],
    dependencies=[Depends(get_current_user)] # !! 所有此路由下的路径都需要登录 !!
)

templates = Jinja2Templates(directory="app/templates")

@router.get("/", response_class=HTMLResponse)
async def admin_dashboard(request: Request, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    websites = crud_website.get_websites(db) # 管理员看到所有网站
    return templates.TemplateResponse("admin/dashboard.html", {
        "request": request,
        "websites": websites,
        "current_user": current_user
    })

# FastAPI 0.100+ 推荐使用 Annotated
# from typing import Annotated
# async def add_website(..., title: Annotated[str, Form()], ...)

@router.post("/website/add")
async def add_website(
    request: Request,
    db: Session = Depends(get_db),
    title: str = Form(...),
    url: str = Form(...), # 可以添加 URL 验证依赖
    description: Optional[str] = Form(None),
    is_public: bool = Form(False) # Checkbox value needs care
):
    # 处理 Checkbox: HTML 表单只会发送选中的值。
    # 如果 checkbox 未选中，`is_public` 不会出现在表单数据中。
    # 一种常见方法是使用隐藏字段，或者检查 `is_public` 是否为 'true' 或 'on'
    # 简单的处理:
    form_data = await request.form()
    is_public_value = True if form_data.get("is_public") else False

    # 数据验证 (Pydantic 可以做得更好)
    try:
        website_in = WebsiteCreate(
            title=title,
            url=url, # Pydantic schema 会自动验证
            description=description,
            is_public=is_public_value
        )
    except Exception as e: # 捕获 Pydantic 验证错误
         # 显示错误，或重定向回表单并带上错误信息
         # return templates.TemplateResponse("admin/dashboard.html", {"request": request, "error": str(e), ...})
         raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=f"Invalid data: {e}")

    crud_website.create_website(db=db, website=website_in)
    # 操作后重定向回管理页面，避免表单重复提交
    return RedirectResponse(url="/admin", status_code=status.HTTP_303_SEE_OTHER)

@router.post("/website/{website_id}/delete")
async def delete_website_entry(
    website_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user) # 确保用户已登录
):
    website = crud_website.get_website(db, website_id)
    if not website:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Website not found")

    # !! 可以添加权限检查，例如只有创建者或管理员能删除 !!

    crud_website.delete_website(db=db, website_id=website_id)
    return RedirectResponse(url="/admin", status_code=status.HTTP_303_SEE_OTHER)

# --- 编辑功能 (未完全实现) ---
# @router.get("/website/{website_id}/edit", response_class=HTMLResponse)
# async def edit_website_form(request: Request, website_id: int, db: Session = Depends(get_db), ...):
#     website = crud_website.get_website(db, website_id)
#     if not website: raise HTTPException(404)
#     # return templates.TemplateResponse("admin/edit_website.html", {"request": request, "website": website, ...})

# @router.post("/website/{website_id}/edit")
# async def update_website_entry(request: Request, website_id: int, db: Session = Depends(get_db), ... form data ...):
#      # ... 获取表单数据 ...
#      # ... 验证数据 ...
#      # ... 调用 crud_website.update_website(...) ...
#      # return RedirectResponse("/admin", status_code=303)