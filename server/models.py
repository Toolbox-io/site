import re
from datetime import datetime

from pydantic import BaseModel, EmailStr, field_validator


# noinspection PyMethodParameters
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

    @field_validator('username')
    def validate_username(cls, v):
        if len(v) < 3:
            raise ValueError('Username must be at least 3 characters long')
        if len(v) > 50:
            raise ValueError('Username must be less than 50 characters')
        if not re.match(r'^[a-zA-Z0-9_-]+$', v):
            raise ValueError('Username can only contain letters, numbers, underscores, and hyphens')
        return v
    
    @field_validator('email')
    def validate_email(cls, v):
        if len(v) > 254:
            raise ValueError('Email is too long')
        return v.lower()


# noinspection PyMethodParameters
class UserLogin(BaseModel):
    username: str
    password: str
    
    @field_validator('username')
    def validate_username(cls, v):
        if len(v) < 1:
            raise ValueError('Username cannot be empty')
        if len(v) > 50:
            raise ValueError('Username is too long')
        return v

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str


# noinspection PyMethodParameters
class PasswordChange(BaseModel):
    current_password: str
    new_password: str
    
    @field_validator('current_password', 'new_password')
    def validate_password_not_empty(cls, v):
        if len(v) < 1:
            raise ValueError('Password cannot be empty')
        return v

class Message(BaseModel):
    message: str 