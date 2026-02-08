from __future__ import annotations

from datetime import datetime
from typing import Optional

from omniprice.models.auth import User


class AuthRepository:
    @staticmethod
    async def get_by_email(email: str) -> Optional[User]:
        return await User.find_one(User.email == email)

    @staticmethod
    async def create(*, email: str, hashed_password: str, full_name: str | None) -> User:
        user = User(email=email, hashed_password=hashed_password, full_name=full_name)
        await user.insert()
        return user

    @staticmethod
    async def touch_updated_at(user: User) -> User:
        await user.set({"updated_at": datetime.utcnow()})
        return user
