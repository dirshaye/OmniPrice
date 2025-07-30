from beanie import Document, Indexed
from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List
from datetime import datetime
from enum import Enum
import uuid

class UserRole(str, Enum):
    ADMIN = "admin"
    VIEWER = "viewer"
    EDITOR = "editor"

class UserStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"

class User(Document):
    """User model for authentication and authorization"""
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), alias="_id")
    username: Indexed(str, unique=True)
    email: Indexed(EmailStr, unique=True)
    hashed_password: str
    full_name: Optional[str] = None
    
    # Role and permissions
    role: UserRole = UserRole.VIEWER
    permissions: List[str] = Field(default_factory=list)
    
    # Status
    is_active: bool = True
    status: UserStatus = UserStatus.ACTIVE
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    last_login: Optional[datetime] = None
    
    # Profile
    avatar_url: Optional[str] = None
    timezone: str = "UTC"
    
    class Settings:
        name = "users"
        indexes = [
            "email",
            "username",
            "role",
            "is_active"
        ]
    
    def __str__(self):
        return f"{self.username} ({self.email})"

class UserCreate(BaseModel):
    """Schema for creating users"""
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=8)
    full_name: Optional[str] = None
    role: UserRole = UserRole.VIEWER

class UserUpdate(BaseModel):
    """Schema for updating users"""
    full_name: Optional[str] = None
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None
    permissions: Optional[List[str]] = None
    avatar_url: Optional[str] = None
    timezone: Optional[str] = None

class UserResponse(BaseModel):
    """Schema for user responses"""
    id: str
    username: str
    email: str
    full_name: Optional[str]
    role: UserRole
    is_active: bool
    status: UserStatus
    created_at: datetime
    last_login: Optional[datetime]
    avatar_url: Optional[str]
    timezone: str

class UserLogin(BaseModel):
    """Schema for user login"""
    username_or_email: str
    password: str

class Token(BaseModel):
    """JWT Token response"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int

class TokenData(BaseModel):
    """Token payload data"""
    username: Optional[str] = None
    user_id: Optional[str] = None
    permissions: List[str] = Field(default_factory=list)
