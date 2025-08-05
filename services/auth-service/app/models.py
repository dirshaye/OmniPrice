from beanie import Document
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum
import uuid

class UserRole(str, Enum):
    ADMIN = "admin"
    USER = "user"
    MANAGER = "manager"

class UserStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"

class User(Document):
    """User model for authentication"""
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), alias="_id")
    
    # Basic info
    email: EmailStr = Field(..., unique=True, index=True)
    username: str = Field(..., unique=True, index=True)
    full_name: str
    
    # Authentication
    hashed_password: str
    is_active: bool = True
    is_verified: bool = False
    
    # Authorization
    role: UserRole = UserRole.USER
    permissions: List[str] = Field(default_factory=list)
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    last_login: Optional[datetime] = None
    
    # Account status
    status: UserStatus = UserStatus.ACTIVE
    
    # Company/tenant info (for multi-tenant)
    company_id: Optional[str] = None
    company_name: Optional[str] = None
    
    class Settings:
        name = "users"
        indexes = [
            "email",
            "username", 
            "company_id",
            "status"
        ]

class RefreshToken(Document):
    """Refresh token model for JWT token management"""
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), alias="_id")
    
    user_id: str = Field(..., index=True)
    token: str = Field(..., unique=True)
    expires_at: datetime
    is_revoked: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Device/session info
    user_agent: Optional[str] = None
    ip_address: Optional[str] = None
    
    class Settings:
        name = "refresh_tokens"
        indexes = [
            "user_id",
            "token",
            "expires_at"
        ]

# Pydantic schemas for API
class UserCreate(BaseModel):
    """Schema for user registration"""
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    full_name: str = Field(..., min_length=1, max_length=100)
    password: str = Field(..., min_length=8, max_length=100)
    company_name: Optional[str] = None

class UserLogin(BaseModel):
    """Schema for user login"""
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    """Schema for user response (without sensitive data)"""
    id: str
    email: EmailStr
    username: str
    full_name: str
    role: UserRole
    is_active: bool
    is_verified: bool
    created_at: datetime
    company_name: Optional[str] = None

class TokenResponse(BaseModel):
    """Schema for JWT token response"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds
    user: UserResponse

class TokenRefresh(BaseModel):
    """Schema for token refresh"""
    refresh_token: str
