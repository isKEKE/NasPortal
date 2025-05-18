from pydantic import BaseModel, HttpUrl
from typing import Optional

class WebsiteBase(BaseModel):
    title: str
    url: HttpUrl # 使用 HttpUrl 进行基本 URL 验证
    description: Optional[str] = None
    is_public: bool = True

class WebsiteCreate(WebsiteBase):
    pass

class Website(WebsiteBase):
    id: int

    class Config:
        from_attributes = True # Pydantic V1 -> from_orm = True in Pydantic V2