from pydantic import BaseModel
from datetime import datetime

class UserBase(BaseModel):
    username: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    username: str
    created_at: datetime
    is_superuser: bool
    is_active: bool

    class Config:
        from_attributes = True # Pydantic V1 -> from_orm = True in Pydantic V2