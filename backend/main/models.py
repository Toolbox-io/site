import re
from datetime import datetime
from sqlalchemy import Boolean, String, DateTime, Column, Integer, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

from pydantic import BaseModel, EmailStr, field_validator

Base = declarative_base()


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


# noinspection PyMethodParameters
class PasswordChange(BaseModel):
    current_password: str
    new_password: str
    
    @field_validator('current_password', 'new_password')
    def validate_password_not_empty(cls, v):
        if len(v) < 1:
            raise ValueError('Password cannot be empty')
        return v


# noinspection PyMethodParameters
class ReportCrash(BaseModel):
    androidVersion: str
    manufacturer: str
    brand: str
    model: str
    programVersion: str

    exceptionClass: str
    exceptionMsg: str
    exceptionStacktrace: str

    whatHappened: str

    @field_validator('whatHappened')
    def validate_whatHappened(cls, v):
        if len(v) > 10000:
            raise ValueError('Field is too long')
        return v

class Message(BaseModel):
    message: str

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    is_verified = Column(Boolean, default=False)
    verification_code = Column(String(6), nullable=True)
    reset_code = Column(String(6), nullable=True)
    reset_token_expiry = Column(DateTime, nullable=True) 

class BlacklistedToken(Base):
    __tablename__ = "blacklisted_tokens"
    id = Column(Integer, primary_key=True, index=True)
    token = Column(String(512), unique=True, nullable=False)
    blacklisted_at = Column(DateTime(timezone=True), server_default=func.now())

class Photo(Base):
    __tablename__ = "photos"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    uuid = Column(String(36), unique=True, index=True, nullable=False)  # Client-generated UUID
    filename = Column(String(255), nullable=False)
    encrypted = Column(Boolean, default=False)  # True if photo is encrypted
    salt = Column(String(64), nullable=True)    # Store as hex/base64 if encrypted
    iv = Column(String(32), nullable=True)      # Store as hex/base64 if encrypted
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())