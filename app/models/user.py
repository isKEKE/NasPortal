import os
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
from sqlalchemy import Boolean, Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from .database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_superuser = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime, nullable=False, default=lambda :datetime.now(timezone.utc).astimezone(ZoneInfo(os.environ["AREA_REGION"])))
    is_active = Column(Boolean, default=True)
    # 可以添加 is_superuser 等字段用于权限控制
    websites = relationship("Website", back_populates="owner", cascade="all, delete", passive_deletes=True)
    tags = relationship("Tag", back_populates="owner", cascade="all, delete", passive_deletes=True)

