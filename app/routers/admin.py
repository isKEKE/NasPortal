from fastapi import APIRouter, Depends, Request, Form, HTTPException, status, Query
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from typing import Annotated, Optional # 使用 Annotated for Form Data in newer FastAPI

from app.models.database import get_db
from app.crud import website as crud_website
from app.crud import user as crud_user
from app.schemas.website import WebsiteCreate, Website # 用于创建和可能的更新验证
from app.schemas.user import User, UserCreate
from app.core.security import get_current_user # 强制登录

router = APIRouter(
    prefix="/admin",
    tags=["admin"],
    dependencies=[Depends(get_current_user)] # !! 所有此路由下的路径都需要登录 !!
)

templates = Jinja2Templates(directory="app/templates")

@router.get("/", response_class=HTMLResponse)
async def admin_dashboard(request: Request, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return templates.TemplateResponse("admin/dashboard.html", {
        "request": request,
        "current_user": current_user
    })

# User ---------------------------------------------------------

@router.get("/user/list", response_model=list[User])
async def get_users(
    request: Request, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=10, ge=1, le=100),
    
):
    if current_user.is_superuser:
        return crud_user.get_all_user(db, skip, limit)
    else:
        return [crud_user.get_user(db, user_id=current_user.id)]


@router.post("/user/add")
async def add_user(
    request: Request,
    db: Session = Depends(get_db),
    username: str = Form(...),
    password: str = Form(...)
):
    user_create = UserCreate(username=username, password=password)

    existing_user = crud_user.get_user_by_username(db, username=username)
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already exists")

    try:
        new_user = crud_user.create_user(db, user_create)
        return {"message": "User created successfully", "user_id": new_user.id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create user: {str(e)}")


@router.delete("/user/delete", status_code=204)
async def deactivate_user(
    request: Request, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    username: str = Form(...)
):
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only superusers can deactivate users."
        )

    user_to_deactivate = crud_user.get_user_by_username(db, username=username)
    if not user_to_deactivate:
        raise HTTPException(status_code=404, detail="User not found")
    if not user_to_deactivate.is_active:
        raise HTTPException(status_code=400, detail="User already deactivated")
    
    crud_user.deactivate_user(db, user_to_deactivate)
    return None


@router.put("/user/edit")
async def edit_user(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    user_id: int = Form(...),
    new_password: str = Form(...),
    is_active: bool = Form(...) 
):
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only superusers can edit users."
        )

    user_to_edit = crud_user.get_user(db, user_id)
    if not user_to_edit:
        raise HTTPException(status_code=404, detail="User not found")

    if new_password and (not crud_user.verify_password(new_password, user_to_edit.hashed_password)):
        user_to_edit.hashed_password = crud_user.get_password_hash(new_password)

    user_to_edit.is_active = is_active

    db.commit()
    db.refresh(user_to_edit)

    return {"message": "User updated successfully"}


# Website ---------------------------------------------------------
@router.get("/website/list", response_model=list[Website]) #  response_model=List[WebsiteOut]
async def get_websites_api(
    request: Request, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, le=1000)
):
    if current_user.is_superuser:
        return crud_website.get_websites(db=db, skip=skip, limit=limit)
    else:
        return crud_website.get_websites_by_user(db=db, user_id=current_user.id, skip=skip, limit=limit)


@router.post("/website/add")
async def add_website(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    title: str = Form(...),
    url: str = Form(...), # 可以添加 URL 验证依赖
    description: Optional[str] = Form(None),
    is_public: bool = Form(False) # Checkbox value needs care
):
    try:
        website_in = WebsiteCreate(
            title=title,
            url=url, # Pydantic schema 会自动验证
            description=description,
            is_public=is_public,
            owner_id=current_user.id
        )
    except Exception as e: # 捕获 Pydantic 验证错误
         raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=f"Invalid data: {e}")

    crud_website.create_website(db=db, website=website_in)
    return {"message": "Website created successfully."}


@router.put("/website/edit")
async def edit_website(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    website_id: int = Form(...),
    title: str = Form(...),
    url: str = Form(...),
    description: str = Form(...),
    is_public: bool = Form(...)
):
    db_website = crud_website.get_website_by_user(db, current_user.id, website_id)
    if not db_website:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Website not found")

    try:
        website_in = WebsiteCreate(
            title=title,
            url=url,
            description=description,
            is_public=is_public,
            owner_id=current_user.id
        )
    except Exception as e:
         raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=f"Invalid data: {e}")
    
    crud_website.update_website(db=db, db_website=db_website, website=website_in)

    return {"message": "Website updated successfully."}


@router.delete("/website/delete")
async def delete_website(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    website_id: int = Form(...)
):
    db_website = crud_website.get_website_by_user(db=db, user_id=current_user.id, website_id=website_id)
    if not db_website:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Website not found")

    crud_website.delete_website(db=db, db_website=db_website)
    return {"message": "Website deleted successfully."}