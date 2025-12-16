from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime

# --------------------------------------
# INCOMING DATA (Requests)
# --------------------------------------

class UserCreate(BaseModel):
    """
    Schema for User Registration
    Technical Note: Pydantic validates types automatically.
    EmailStr ensures it's a valid email format.
    """
    email: EmailStr
    password: str = Field(..., min_length=8, description="Password must be at least 8 chars")
    full_name: Optional[str] = None

class UserLogin(BaseModel):
    """Schema for User Login"""
    email: EmailStr
    password: str

# --------------------------------------
# OUTGOING DATA (Responses)
# --------------------------------------

class UserResponse(BaseModel):
    """
    Schema for returning User data.
    CRITICAL: We do NOT include the 'password' field here.
    """
    id: str = Field(alias="_id") # Map MongoDB '_id' to 'id'
    email: EmailStr
    full_name: Optional[str] = None
    is_active: bool
    created_at: datetime

    class Config:
        # Allows Pydantic to read data from Beanie/ORM objects
        from_attributes = True 
        populate_by_name = True

class Token(BaseModel):
    """Schema for the JWT Token response"""
    access_token: str
    token_type: str = "bearer"
