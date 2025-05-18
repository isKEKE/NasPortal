from sqlalchemy import Boolean, Column, Integer, String, Text
from .database import Base

class Website(Base):
    __tablename__ = "websites"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True, nullable=False)
    url = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    is_public = Column(Boolean, default=True) # True 对所有人可见, False 仅登录可见
    # owner_id = Column(Integer, ForeignKey("users.id")) # 如果需要关联创建者
    # owner = relationship("User")