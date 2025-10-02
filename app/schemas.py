from pydantic import BaseModel, ConfigDict, field_validator
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    email: str
    login: str

class UserCreate(UserBase):
    password: str
    password_confirm: str

    @field_validator('password_confirm')
    @classmethod
    def passwords_match(cls, v, info):
        if 'password' in info.data and v != info.data['password']:
            raise ValueError('passwords do not match')
        return v

    @field_validator('password')
    @classmethod
    def password_length(cls, v):
        if len(v) < 6:
            raise ValueError('password must be at least 6 characters')
        return v

class UserUpdate(BaseModel):
    email: Optional[str] = None
    login: Optional[str] = None

class UserResponse(UserBase):
    id: int
    createdAt: datetime
    updatedAt: datetime
    model_config = ConfigDict(from_attributes=True)

class PostBase(BaseModel):
    title: str
    content: str

class PostCreate(PostBase):
    @field_validator('title')
    @classmethod
    def title_length(cls, v):
        if len(v) < 1:
            raise ValueError('title cannot be empty')
        return v

    @field_validator('content')
    @classmethod
    def content_length(cls, v):
        if len(v) < 10:
            raise ValueError('content must be at least 10 characters')
        return v

class PostUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None

class PostResponse(PostBase):
    id: int
    authorId: int
    createdAt: datetime
    updatedAt: datetime
    likes: int = 0
    views: int = 0
    model_config = ConfigDict(from_attributes=True)