import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = os.getenv("POSTFRES_DB_URL") # 使用 SQLite 示例

engine = create_engine(
    SQLALCHEMY_DATABASE_URL
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# !! 需要手动创建数据库表 !!
# 可以使用 Alembic 管理，或者在 main.py 启动时创建 (不推荐生产)
# Base.metadata.create_all(bind=engine) # 在 main.py 中调用一次来创建表