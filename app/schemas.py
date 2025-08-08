from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime, date


# User schemas
class UserBase(BaseModel):
    email: EmailStr

class UserCreate(UserBase):
    password: str = Field(..., min_length=6, description="Password must be at least 6 characters")

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = None

class UserRead(UserBase):
    id: int
    is_active: bool
    created_at: Optional[datetime]

    class Config:
        from_attributes = True

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str
    user: UserRead

class TokenRefresh(BaseModel):
    refresh_token: str


# Post schemas
class PostBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    content: str = Field(..., min_length=1)
    auto_reply_enabled: Optional[bool] = False
    auto_reply_delay: Optional[int] = Field(60, ge=0, le=3600)  # 0-3600 секунд

class PostCreate(PostBase):
    pass

class PostUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    content: Optional[str] = Field(None, min_length=1)
    auto_reply_enabled: Optional[bool] = None
    auto_reply_delay: Optional[int] = Field(None, ge=0, le=3600)

class PostRead(PostBase):
    id: int
    author_id: int
    created_at: Optional[datetime]
    comments_count: Optional[int] = 0

    class Config:
        from_attributes = True

class PostList(BaseModel):
    posts: List[PostRead]
    total: int
    page: int
    page_size: int
    pages: int


# Comment schemas
class CommentBase(BaseModel):
    content: str = Field(..., min_length=1, max_length=1000)

class CommentCreate(CommentBase):
    pass

class CommentUpdate(BaseModel):
    content: str = Field(..., min_length=1, max_length=1000)

class CommentRead(CommentBase):
    id: int
    author_id: int
    post_id: int
    created_at: Optional[datetime]
    is_blocked: bool = False
    author_email: Optional[str] = None

    class Config:
        from_attributes = True

class CommentList(BaseModel):
    comments: List[CommentRead]
    total: int
    page: int
    page_size: int
    pages: int


# Analytics schemas
class CommentsDailyBreakdown(BaseModel):
    date: date
    total_comments: int
    blocked_comments: int
    active_comments: int

class AnalyticsResponse(BaseModel):
    period: str
    data: List[CommentsDailyBreakdown]
    summary: dict


class ErrorResponse(BaseModel):
    detail: str
    error_code: Optional[str] = None


class PaginationParams(BaseModel):
    page: int = Field(1, ge=1)
    page_size: int = Field(10, ge=1, le=100)
