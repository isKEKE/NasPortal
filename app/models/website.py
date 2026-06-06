from sqlalchemy import Boolean, Column, Integer, String, Text, ForeignKey, Table
from sqlalchemy.orm import relationship
from .database import Base
from .association import website_tags


class Website(Base):
    __tablename__ = "websites"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title = Column(String, index=True, nullable=False)
    url = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    is_public = Column(Boolean, default=True)

    owner_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    owner = relationship("User", back_populates="websites", passive_deletes=True)
    tags = relationship("Tag", secondary=website_tags, back_populates="websites")



