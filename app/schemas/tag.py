from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field, field_serializer

from app.schemas.user import User
from app.schemas.website import Website


class TagBase(BaseModel):
    name: str
    owner: Optional[User] = Field(default=None, exclude=True)


class TagCreate(TagBase):
    owner_id: int


class Tag(TagBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    owner_username: Optional[str] = None
    websites: List[Website] = Field(default_factory=list)

    @field_serializer("owner_username")
    def serialize_owner_username(self, value):
        return self.owner.username if self.owner else None
