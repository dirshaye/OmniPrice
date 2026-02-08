from fastapi import HTTPException, status

from omniprice.core.security import create_access_token, hash_password, verify_password
from omniprice.repositories.auth import AuthRepository
from omniprice.schemas.auth import UserCreate


class AuthService:
    @staticmethod
    async def register_user(user_data: UserCreate):
        existing_user = await AuthRepository.get_by_email(user_data.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )

        hashed_pw = hash_password(user_data.password)
        return await AuthRepository.create(
            email=user_data.email,
            hashed_password=hashed_pw,
            full_name=user_data.full_name,
        )

    @staticmethod
    async def authenticate_user(email: str, password: str):
        user = await AuthRepository.get_by_email(email)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user

    @staticmethod
    def create_token(user) -> dict:
        access_token = create_access_token(data={"sub": user.email})
        return {"access_token": access_token, "token_type": "bearer"}

    @staticmethod
    async def get_user_by_email(email: str):
        user = await AuthRepository.get_by_email(email)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )
        return user
