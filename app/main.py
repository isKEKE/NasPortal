from fastapi import FastAPI, Depends, Request
from fastapi.staticfiles import StaticFiles # 如果需要 FastAPI 托管静态文件
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session # 仅用于创建表（如果需要）

from app.routers import auth, portal, admin
from app.models import user, website # 导入模型
from app.models.database import engine, Base, get_db # 导入数据库引擎和 Base
# from app.core.security import get_current_user_optional # 如果需要在 main 中使用


app = FastAPI(title="Portal")

app.mount("/static", StaticFiles(directory="app/static"), name="static")

app.include_router(portal.router)
app.include_router(auth.router)
app.include_router(admin.router)



# --- 包含路由 ---


# app.include_router(admin.router)

# --- 根路径 (可以重定向或与 portal.router 中的 '/' 冲突, 这里移到 portal.router) ---
# @app.get("/", response_class=HTMLResponse)
# async def read_root(request: Request, db: Session = Depends(get_db), current_user = Depends(get_current_user_optional)):
#     # 可以在这里渲染主页，或者直接使用 portal router 的 "/"
#     # ... (逻辑与 portal.py 中的类似) ...
#     pass

# print("FastAPI application started. Routers included.")
# print("Run with: uvicorn app.main:app --reload")