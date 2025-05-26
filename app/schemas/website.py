from pydantic import BaseModel, HttpUrl, field_serializer, Field
from typing import Optional
from app.schemas.user import User


class WebsiteBase(BaseModel):
    title: str
    url: HttpUrl
    description: Optional[str] = None
    is_public: bool = True
    owner: Optional[User] = Field(default=None, exclude=True)


class WebsiteCreate(WebsiteBase):
    owner_id: int


class Website(WebsiteBase):
    id: int
    owner_username: Optional[str] = None

    # Added the 'value' argument to the field_serializer signature
    @field_serializer("owner_username")
    def serialize_owner_username(self, value):
        # The logic remains the same, accessing the owner from self
        return self.owner.username if self.owner else None

    class Config:
        from_attributes = True
        fields = {
            'owner': {'exclude': True}
        }

