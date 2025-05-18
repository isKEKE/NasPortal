import os
from pathlib import Path

# 项目目录结构定义
structure = [
    "app/__init__.py",
    "app/main.py",
    "app/routers/__init__.py",
    "app/routers/auth.py",
    "app/routers/portal.py",
    "app/routers/admin.py",
    "app/templates/base.html",
    "app/templates/login.html",
    "app/templates/portal.html",
    "app/templates/admin/dashboard.html",
    "app/static",  # 空目录，说明可自行添加资源
    "app/core/__init__.py",
    "app/core/config.py",
    "app/core/security.py",
    "app/models/__init__.py",
    "app/models/database.py",
    "app/models/user.py",
    "app/models/website.py",
    "app/schemas/__init__.py",
    "app/schemas/user.py",
    "app/schemas/website.py",
    "app/crud/__init__.py",
    "app/crud/user.py",
    "app/crud/website.py",
    "alembic",  # 空目录
    "alembic.ini",
    "run.py",
]

def create_structure(base_path="."):
    for path_str in structure:
        path = Path(base_path) / path_str
        if path.suffix:  # 是文件
            path.parent.mkdir(parents=True, exist_ok=True)
            path.touch(exist_ok=True)
            print(f"Created file: {path}")
        else:  # 是目录
            path.mkdir(parents=True, exist_ok=True)
            print(f"Created directory: {path}")

if __name__ == "__main__":
    # create_structure(".")
    ...
