from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from passlib.context import CryptContext
from jose import JWTError, jwt
from fastapi import HTTPException, status
from pydantic import ValidationError
import secrets
import hashlib

from .models import User, RefreshToken, UserCreate, UserLogin, TokenResponse, UserResponse

class AuthService:
    """Authentication service with JWT and password management"""
    
    def __init__(self, secret_key: str, algorithm: str = "HS256"):
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        self.access_token_expire_minutes = 30
        self.refresh_token_expire_days = 7
    
    # Password utilities
    def hash_password(self, password: str) -> str:
        """Hash a password using bcrypt"""
        return self.pwd_context.hash(password)
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash"""
        return self.pwd_context.verify(plain_password, hashed_password)
    
    # JWT token utilities
    def create_access_token(self, data: Dict[str, Any]) -> str:
        """Create JWT access token"""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
        to_encode.update({"exp": expire, "type": "access"})
        
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt
    
    def create_refresh_token(self, user_id: str) -> str:
        """Create refresh token (random string)"""
        token_data = f"{user_id}:{datetime.utcnow().isoformat()}:{secrets.token_hex(32)}"
        return hashlib.sha256(token_data.encode()).hexdigest()
    
    def verify_token(self, token: str) -> Dict[str, Any]:
        """Verify and decode JWT token"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
    
    # User authentication methods
    async def register_user(self, user_data: UserCreate) -> User:
        """Register a new user"""
        # Check if user already exists
        existing_user = await User.find_one(
            {"$or": [{"email": user_data.email}, {"username": user_data.username}]}
        )
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this email or username already exists"
            )
        
        # Create new user
        hashed_password = self.hash_password(user_data.password)
        user = User(
            email=user_data.email,
            username=user_data.username,
            full_name=user_data.full_name,
            hashed_password=hashed_password,
            company_name=user_data.company_name,
        )
        
        await user.save()
        return user
    
    async def authenticate_user(self, login_data: UserLogin) -> Optional[User]:
        """Authenticate user with email and password"""
        user = await User.find_one({"email": login_data.email})
        if not user or not self.verify_password(login_data.password, user.hashed_password):
            return None
        
        # Update last login
        user.last_login = datetime.utcnow()
        await user.save()
        
        return user
    
    async def login_user(self, login_data: UserLogin, user_agent: str = None, ip_address: str = None) -> TokenResponse:
        """Login user and create tokens"""
        user = await self.authenticate_user(login_data)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password"
            )
        
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User account is inactive"
            )
        
        # Create tokens
        access_token_data = {
            "sub": user.id,
            "email": user.email,
            "role": user.role,
            "company_id": user.company_id
        }
        access_token = self.create_access_token(access_token_data)
        refresh_token = self.create_refresh_token(user.id)
        
        # Save refresh token
        refresh_token_doc = RefreshToken(
            user_id=user.id,
            token=refresh_token,
            expires_at=datetime.utcnow() + timedelta(days=self.refresh_token_expire_days),
            user_agent=user_agent,
            ip_address=ip_address
        )
        await refresh_token_doc.save()
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=self.access_token_expire_minutes * 60,
            user=UserResponse(
                id=user.id,
                email=user.email,
                username=user.username,
                full_name=user.full_name,
                role=user.role,
                is_active=user.is_active,
                is_verified=user.is_verified,
                created_at=user.created_at,
                company_name=user.company_name
            )
        )
    
    async def refresh_access_token(self, refresh_token: str) -> TokenResponse:
        """Refresh access token using refresh token"""
        token_doc = await RefreshToken.find_one({"token": refresh_token})
        
        if not token_doc or token_doc.is_revoked:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
        
        if token_doc.expires_at < datetime.utcnow():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token expired"
            )
        
        # Get user
        user = await User.get(token_doc.user_id)
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive"
            )
        
        # Create new access token
        access_token_data = {
            "sub": user.id,
            "email": user.email,
            "role": user.role,
            "company_id": user.company_id
        }
        access_token = self.create_access_token(access_token_data)
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,  # Keep same refresh token
            expires_in=self.access_token_expire_minutes * 60,
            user=UserResponse(
                id=user.id,
                email=user.email,
                username=user.username,
                full_name=user.full_name,
                role=user.role,
                is_active=user.is_active,
                is_verified=user.is_verified,
                created_at=user.created_at,
                company_name=user.company_name
            )
        )
    
    async def logout_user(self, refresh_token: str) -> bool:
        """Logout user by revoking refresh token"""
        token_doc = await RefreshToken.find_one({"token": refresh_token})
        if token_doc:
            token_doc.is_revoked = True
            await token_doc.save()
            return True
        return False
    
    async def get_current_user(self, token: str) -> User:
        """Get current user from JWT token"""
        payload = self.verify_token(token)
        user_id = payload.get("sub")
        
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials"
            )
        
        user = await User.get(user_id)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )
        
        return user
