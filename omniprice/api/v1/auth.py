from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from omniprice.modules.auth.schemas import UserCreate, UserResponse, Token, UserLogin
from omniprice.modules.auth.service import AuthService

router = APIRouter()

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate):
    """
    Register a new user.
    
    - **email**: Valid email address
    - **password**: Min 8 chars
    - **full_name**: Optional
    """
    return await AuthService.register_user(user_data)

@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Login to get an access token.
    
    Technical Note: 
    We use OAuth2PasswordRequestForm which expects form-data:
    - username (email)
    - password
    This is standard for Swagger UI compatibility.
    """
    user = await AuthService.authenticate_user(form_data.username, form_data.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    return AuthService.create_token(user)

@router.post("/login/json", response_model=Token)
async def login_json(user_data: UserLogin):
    """
    Alternative Login endpoint accepting JSON body.
    Easier for React Frontend to use.
    """
    user = await AuthService.authenticate_user(user_data.email, user_data.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    return AuthService.create_token(user)

