from fastapi import APIRouter, Depends, Request, Form, HTTPException, status, Query
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from typing import Annotated, Optional

from app.models.database import get_db
from app.crud import website as crud_website, user as crud_user, tag as crud_tag
from app.schemas.website import WebsiteCreate, Website
from app.schemas.user import User, UserCreate
from app.schemas.tag import Tag, TagCreate
from app.core.security import get_current_user

router = APIRouter(
    prefix="/admin", tags=["admin"], dependencies=[Depends(get_current_user)]
)

templates = Jinja2Templates(directory="app/templates")


class AdminRouter:
    def __init__(
        self,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
    ):
        self.db = db
        self.current_user = current_user

    # User Routes
    async def get_users(self, skip: int = 0, limit: int = 10):
        if self.current_user.is_superuser:
            return crud_user.get_all_user(self.db, skip, limit)
        else:
            return [crud_user.get_user(self.db, user_id=self.current_user.id)]

    async def add_user(self, username: str, password: str):
        user_create = UserCreate(username=username, password=password)
        existing_user = crud_user.get_user_by_username(self.db, username=username)
        if existing_user:
            raise HTTPException(status_code=400, detail="Username already exists")
        try:
            new_user = crud_user.create_user(self.db, user_create)
            return {"message": "User created successfully", "user_id": new_user.id}
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Failed to create user: {str(e)}"
            )

    async def edit_user(self, user_id: int, new_password: str, is_active: bool):
        if not self.current_user.is_superuser:
            raise HTTPException(
                status_code=403, detail="Only superusers can edit users."
            )
        user_to_edit = crud_user.get_user(self.db, user_id)
        if not user_to_edit:
            raise HTTPException(status_code=404, detail="User not found")
        if new_password and (
            not crud_user.verify_password(new_password, user_to_edit.hashed_password)
        ):
            user_to_edit.hashed_password = crud_user.get_password_hash(new_password)
        user_to_edit.is_active = is_active
        self.db.commit()
        self.db.refresh(user_to_edit)
        return {"message": "User updated successfully"}

    async def deactivate_user(self, username: str):
        if not self.current_user.is_superuser:
            raise HTTPException(
                status_code=403, detail="Only superusers can deactivate users."
            )
        user_to_deactivate = crud_user.get_user_by_username(self.db, username=username)
        if not user_to_deactivate:
            raise HTTPException(status_code=404, detail="User not found")
        if not user_to_deactivate.is_active:
            raise HTTPException(status_code=400, detail="User already deactivated")
        crud_user.deactivate_user(self.db, user_to_deactivate)
        return None

    # Website Routes
    async def get_websites(self, skip: int = 0, limit: int = 10):
        if self.current_user.is_superuser:
            return crud_website.get_websites(db=self.db, skip=skip, limit=limit)
        else:
            return crud_website.get_websites_by_user(
                db=self.db, user_id=self.current_user.id, skip=skip, limit=limit
            )

    async def add_website(
        self,
        title: str,
        url: str,
        description: Optional[str] = None,
        is_public: bool = False,
    ):
        try:
            website_in = WebsiteCreate(
                title=title,
                url=url,
                description=description,
                is_public=is_public,
                owner_id=self.current_user.id,
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Invalid data: {e}",
            )
        crud_website.create_website(db=self.db, website=website_in)
        return {"message": "Website created successfully."}

    async def edit_website(
        self, website_id: int, title: str, url: str, description: str, is_public: bool
    ):
        db_website = crud_website.get_website_by_user(
            self.db, self.current_user.id, website_id
        )
        if not db_website:
            raise HTTPException(status_code=404, detail="Website not found")
        try:
            website_in = WebsiteCreate(
                title=title,
                url=url,
                description=description,
                is_public=is_public,
                owner_id=self.current_user.id,
            )
        except Exception as e:
            raise HTTPException(status_code=422, detail=f"Invalid data: {e}")
        crud_website.update_website(
            db=self.db, db_website=db_website, website=website_in
        )
        return {"message": "Website updated successfully."}

    async def delete_website(self, website_id: int):
        db_website = crud_website.get_website_by_user(
            self.db, self.current_user.id, website_id
        )
        if not db_website:
            raise HTTPException(status_code=404, detail="Website not found")
        crud_website.delete_website(db=self.db, db_website=db_website)
        return {"message": "Website deleted successfully."}

    # Tag Routes
    async def get_tags(self, skip: int = 0, limit: int = 10):
        return crud_tag.get_tags_by_owner(
            db=self.db, owner_id=self.current_user.id, skip=skip, limit=limit
        )
    
    async def add_tags(
        self,
        tag_name: str
    ):
        try:
            tag_in = TagCreate(name=tag_name, owner_id=self.current_user.id)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Invalid data: {e}",
            )
        crud_tag.create_tag(db=self.db, tag=tag_in)
        return {"message": "Website created successfully."}


# Register routes
admin_router = AdminRouter()


@router.get("/", response_class=HTMLResponse)
async def admin_dashboard(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return templates.TemplateResponse(
        request,
        "admin/dashboard.html",
        {"request": request, "current_user": current_user},
    )


@router.get("/user/list", response_model=list[User])
async def get_users(
    request: Request,
    admin: AdminRouter = Depends(AdminRouter),
    skip: int = Query(0),
    limit: int = Query(10),
):
    return await admin.get_users(skip, limit)


@router.post("/user/add")
async def add_user(
    request: Request,
    admin: AdminRouter = Depends(AdminRouter),
    username: str = Form(...),
    password: str = Form(...),
):
    return await admin.add_user(username, password)


@router.put("/user/edit")
async def edit_user(
    request: Request,
    admin: AdminRouter = Depends(AdminRouter),
    user_id: int = Form(...),
    new_password: str = Form(...),
    is_active: bool = Form(...),
):
    return await admin.edit_user(user_id, new_password, is_active)


@router.delete("/user/delete", status_code=204)
async def deactivate_user(
    request: Request,
    admin: AdminRouter = Depends(AdminRouter),
    username: str = Form(...),
):
    return await admin.deactivate_user(username)


@router.get("/website/list", response_model=list[Website])
async def get_websites_api(
    request: Request,
    admin: AdminRouter = Depends(AdminRouter),
    skip: int = Query(0),
    limit: int = Query(10),
):
    return await admin.get_websites(skip, limit)


@router.post("/website/add")
async def add_website(
    request: Request,
    admin: AdminRouter = Depends(AdminRouter),
    title: str = Form(...),
    url: str = Form(...),
    description: Optional[str] = Form(None),
    is_public: bool = Form(False),
):
    return await admin.add_website(title, url, description, is_public)


@router.put("/website/edit")
async def edit_website(
    request: Request,
    admin: AdminRouter = Depends(AdminRouter),
    website_id: int = Form(...),
    title: str = Form(...),
    url: str = Form(...),
    description: str = Form(...),
    is_public: bool = Form(...),
):
    return await admin.edit_website(website_id, title, url, description, is_public)


@router.delete("/website/delete")
async def delete_website(
    request: Request,
    admin: AdminRouter = Depends(AdminRouter),
    website_id: int = Form(...),
):
    return await admin.delete_website(website_id)


@router.get("/tag/list", response_model=list[Tag])
async def get_websites_api(
    request: Request,
    admin: AdminRouter = Depends(AdminRouter),
    skip: int = Query(0),
    limit: int = Query(10),
):
    return await admin.get_tags(skip, limit)


@router.post("/tag/add")
async def add_website(
    request: Request,
    admin: AdminRouter = Depends(AdminRouter),
    new_tag_name: str = Form(...),
):
    return await admin.add_tags(new_tag_name)
