from typing import Optional
from datetime import datetime
from beanie import Document, Indexed
from pydantic import Field, EmailStr
import pymongo

class User(Document):
    """
    User model representing a registered user in the system.
    
    Attributes:
        email: Unique email address (Indexed)
        hashed_password: Bcrypt hashed password string
        full_name: User's display name
        is_active: Boolean flag for account status
        is_superuser: Boolean flag for admin privileges
        created_at: Timestamp of registration
        updated_at: Timestamp of last update
    """
    email: Indexed(EmailStr, unique=True) # type: ignore
    hashed_password: str
    full_name: Optional[str] = None
    is_active: bool = True
    is_superuser: bool = False
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "users"  # MongoDB collection name
        
    def __repr__(self) -> str:
        return f"<User {self.email}>"
