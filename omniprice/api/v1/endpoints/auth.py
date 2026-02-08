from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from omniprice.core.ratelimit import rate_limit_dependency
from omniprice.core.security import get_current_user_id
from omniprice.schemas.auth import Token, UserCreate, UserLogin, UserResponse
from omniprice.services.auth import AuthService

router = APIRouter()


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(rate_limit_dependency(namespace="auth_register", max_requests=5, window_seconds=60))],
)
async def register(user_data: UserCreate):
    """
    Register a new user.
    """
    user = await AuthService.register_user(user_data)
    return UserResponse(
        id=str(user.id),
        email=user.email,
        full_name=user.full_name,
        is_active=user.is_active,
        created_at=user.created_at,
    )


@router.post(
    "/login",
    response_model=Token,
    dependencies=[Depends(rate_limit_dependency(namespace="auth_login", max_requests=8, window_seconds=60))],
)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    JWT login endpoint using form payload (username/password).
    """
    user = await AuthService.authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
    )
    return AuthService.create_token(user)


@router.post(
    "/token",
    response_model=Token,
    dependencies=[Depends(rate_limit_dependency(namespace="auth_token", max_requests=8, window_seconds=60))],
)
async def token(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    OAuth2 password-flow compatible token endpoint for JWT clients.
    """
    return await login(form_data)


@router.post(
    "/login/json",
    response_model=Token,
    dependencies=[Depends(rate_limit_dependency(namespace="auth_login_json", max_requests=8, window_seconds=60))],
)
async def login_json(user_data: UserLogin):
    """
    Login endpoint using JSON payload for frontend clients.
    """
    user = await AuthService.authenticate_user(user_data.email, user_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
    )
    return AuthService.create_token(user)


@router.get("/me", response_model=UserResponse)
async def get_me(current_subject: str = Depends(get_current_user_id)):
    """
    Return current authenticated user (JWT only).
    """
    user = await AuthService.get_user_by_email(current_subject)
    return UserResponse(
        id=str(user.id),
        email=user.email,
        full_name=user.full_name,
        is_active=user.is_active,
        created_at=user.created_at,
    )
