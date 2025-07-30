from beanie import Document
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class User(Document):
    username: str
    email: EmailStr
    full_name: Optional[str] = None
    hashed_password: str
    is_active: bool = True
    is_staff: bool = False
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()

    class Settings:
        name = "users"
