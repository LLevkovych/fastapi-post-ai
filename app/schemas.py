from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


class UserBase(BaseModel):
    email: EmailStr

class UserCreate(UserBase):
    password: str

class UserRead(UserBase):
    id: int
    is_active: bool
    created_at: Optional[datetime]

    class Config:
        orm_mode = True


class PostBase(BaseModel):
    title: str
    content: str
    auto_reply_enabled: Optional[bool] = False
    auto_reply_delay: Optional[int] = 60

class PostCreate(PostBase):
    pass

class PostRead(PostBase):
    id: int
    author_id: int
    created_at: Optional[datetime]

    class Config:
        orm_mode = True


class CommentBase(BaseModel):
    content: str

class CommentCreate(CommentBase):
    pass

class CommentRead(CommentBase):
    id: int
    author_id: int
    post_id: int
    created_at: Optional[datetime]
    is_blocked: Optional[bool]

    class Config:
        orm_mode = True
