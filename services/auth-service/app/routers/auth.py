from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional

from ..auth import AuthService
from ..models import UserCreate, UserLogin, TokenResponse, UserResponse
from ..config import get_settings

# Initialize router
router = APIRouter(prefix="/auth", tags=["authentication"])

# Security scheme for Bearer token
security = HTTPBearer()

# Get settings and initialize auth service
settings = get_settings()
auth_service = AuthService(secret_key=settings.SECRET_KEY)

# Dependency to get current user
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Dependency to get current authenticated user"""
    token = credentials.credentials
    return await auth_service.get_current_user(token)

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate):
    """
    Register a new user
    
    - **email**: Valid email address (must be unique)
    - **username**: Username (must be unique)
    - **full_name**: User's full name
    - **password**: Strong password (min 8 characters)
    - **company_name**: Optional company name
    """
    try:
        user = await auth_service.register_user(user_data)
        return UserResponse(
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
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Registration failed: {str(e)}"
        )

@router.post("/login", response_model=TokenResponse)
async def login(login_data: UserLogin, request: Request):
    """
    Login user and get access tokens
    
    - **email**: User's email address
    - **password**: User's password
    
    Returns access token and refresh token for authentication
    """
    try:
        # Extract client info for token tracking
        user_agent = request.headers.get("user-agent")
        client_host = request.client.host if request.client else None
        
        tokens = await auth_service.login_user(
            login_data=login_data,
            user_agent=user_agent,
            ip_address=client_host
        )
        return tokens
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Login failed: {str(e)}"
        )

@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(refresh_request: dict):
    """
    Refresh access token using refresh token
    
    - **refresh_token**: Valid refresh token
    
    Returns new access token with same refresh token
    """
    refresh_token = refresh_request.get("refresh_token")
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Refresh token is required"
        )
    
    try:
        tokens = await auth_service.refresh_access_token(refresh_token)
        return tokens
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Token refresh failed: {str(e)}"
        )

@router.post("/logout", status_code=status.HTTP_200_OK)
async def logout(logout_request: dict, current_user=Depends(get_current_user)):
    """
    Logout user by revoking refresh token
    
    - **refresh_token**: Refresh token to revoke
    
    Requires valid access token in Authorization header
    """
    refresh_token = logout_request.get("refresh_token")
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Refresh token is required"
        )
    
    try:
        success = await auth_service.logout_user(refresh_token)
        if success:
            return {"message": "Successfully logged out"}
        else:
            return {"message": "Refresh token not found or already revoked"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Logout failed: {str(e)}"
        )

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user=Depends(get_current_user)):
    """
    Get current user information
    
    Requires valid access token in Authorization header
    Returns user profile information
    """
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        username=current_user.username,
        full_name=current_user.full_name,
        role=current_user.role,
        is_active=current_user.is_active,
        is_verified=current_user.is_verified,
        created_at=current_user.created_at,
        company_name=current_user.company_name
    )

@router.get("/health", status_code=status.HTTP_200_OK)
async def health_check():
    """
    Health check endpoint for service monitoring
    """
    return {
        "status": "healthy",
        "service": "auth-service",
        "version": "1.0.0"
    }

# Additional utility endpoints
@router.post("/verify-token", status_code=status.HTTP_200_OK)
async def verify_token(token_request: dict):
    """
    Verify if an access token is valid
    
    - **token**: JWT access token to verify
    
    Returns token validity and user info
    """
    token = token_request.get("token")
    if not token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token is required"
        )
    
    try:
        payload = auth_service.verify_token(token)
        return {
            "valid": True,
            "user_id": payload.get("sub"),
            "email": payload.get("email"),
            "role": payload.get("role"),
            "expires": payload.get("exp")
        }
    except HTTPException:
        return {"valid": False, "error": "Invalid or expired token"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Token verification failed: {str(e)}"
        )
