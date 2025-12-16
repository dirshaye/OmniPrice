from fastapi import HTTPException, status
from omniprice.modules.auth.models import User
from omniprice.modules.auth.schemas import UserCreate
from omniprice.core.security import hash_password, verify_password, create_access_token

class AuthService:
    """
    Business Logic for Authentication
    Separates 'How it works' (Logic) from 'How it's called' (API)
    """

    @staticmethod
    async def register_user(user_data: UserCreate) -> User:
        """
        Register a new user
        1. Check if email already exists
        2. Hash the password (NEVER save plain text)
        3. Save to MongoDB
        """
        # Step 1: Check for duplicates
        existing_user = await User.find_one(User.email == user_data.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )

        # Step 2: Hash password
        hashed_pw = hash_password(user_data.password)

        # Step 3: Create User instance
        new_user = User(
            email=user_data.email,
            hashed_password=hashed_pw,
            full_name=user_data.full_name
        )
        
        # Step 4: Save to DB (Beanie magic)
        await new_user.create()
        
        return new_user

    @staticmethod
    async def authenticate_user(email: str, password: str) -> User:
        """
        Verify credentials for login
        1. Find user by email
        2. Verify password hash matches
        """
        user = await User.find_one(User.email == email)
        
        if not user:
            return None
            
        if not verify_password(password, user.hashed_password):
            return None
            
        return user

    @staticmethod
    def create_token(user: User) -> dict:
        """
        Generate JWT token for a user
        """
        access_token = create_access_token(
            data={"sub": user.email}
        )
        return {"access_token": access_token, "token_type": "bearer"}
