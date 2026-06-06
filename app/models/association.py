from sqlalchemy import Column, Integer, ForeignKey, Table
from .database import Base

website_tags = Table(
    "website_tags",
    Base.metadata,
    Column("website_id", Integer, ForeignKey("websites.id", ondelete="CASCADE")),
    Column("tag_id", Integer, ForeignKey("tags.id", ondelete="CASCADE"))
)