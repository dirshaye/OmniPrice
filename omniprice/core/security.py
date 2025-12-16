"""
Security Module - Authentication & Authorization

Technical Explanation:
- JWT (JSON Web Tokens) for stateless authentication
- Password hashing using bcrypt (secure one-way encryption)
- No password is stored in plain text (industry standard!)
- Tokens contain user data, reducing database lookups
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import logging

from omniprice.core.config import settings

logger = logging.getLogger(__name__)

# Password hashing context
# Technical Note: bcrypt is a slow hashing algorithm (intentional!)
# This prevents brute-force attacks - takes ~100ms to hash
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# HTTP Bearer token scheme for FastAPI
# Technical Note: This extracts "Bearer <token>" from Authorization header
security = HTTPBearer()


def hash_password(password: str) -> str:
    """
    Hash a plain text password
    
    Technical Explanation:
    - Uses bcrypt with salt (random data added to password)
    - Same password produces different hashes each time (salt is random)
    - Hash is one-way: you can't reverse it to get original password
    
    Usage:
        hashed = hash_password("user_password123")
        # Store hashed password in database, NOT plain text!
    
    Args:
        password: Plain text password
    
    Returns:
        Hashed password string (60 characters)
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against its hash
    
    Technical Explanation:
    - Hashes plain_password with same salt from hashed_password
    - Compares results - if match, password is correct
    - Takes ~100ms intentionally (prevents brute force)
    
    Usage:
        # During login
        if verify_password(user_input, db_hash):
            # Password correct!
        else:
            # Wrong password
    
    Args:
        plain_password: User's input password
        hashed_password: Stored hash from database
    
    Returns:
        True if password matches, False otherwise
    """
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception as e:
        logger.error(f"Password verification error: {e}")
        return False


def create_access_token(
    data: Dict[str, Any], 
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    Create a JWT access token
    
    Technical Explanation:
    - JWT = Header.Payload.Signature
    - Header: Algorithm (HS256)
    - Payload: User data (sub=user_id, exp=expiry, etc.)
    - Signature: HMAC(Header + Payload, SECRET_KEY)
    - Anyone can decode payload, but only server can verify signature
    
    Token Flow:
    1. User logs in with email/password
    2. Server verifies credentials
    3. Server creates JWT with user_id
    4. Client stores token (localStorage/cookie)
    5. Client sends token in Authorization header for future requests
    6. Server verifies token signature and checks expiry
    
    Args:
        data: Dictionary to encode (usually {"sub": user_id})
        expires_delta: Token lifetime (default: 30 minutes)
    
    Returns:
        JWT token string
    
    Usage:
        token = create_access_token({"sub": user.id})
        # Return to client
    """
    to_encode = data.copy()
    
    # Set expiration time
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    
    # Add standard JWT claims
    to_encode.update({
        "exp": expire,  # Expiration time
        "iat": datetime.utcnow(),  # Issued at
        "type": "access"
    })
    
    # Create JWT
    # Technical Note: SECRET_KEY must be kept secret!
    # If leaked, attackers can create valid tokens
    encoded_jwt = jwt.encode(
        to_encode, 
        settings.SECRET_KEY, 
        algorithm=settings.ALGORITHM
    )
    
    return encoded_jwt


def create_refresh_token(data: Dict[str, Any]) -> str:
    """
    Create a JWT refresh token
    
    Technical Explanation:
    - Refresh tokens have longer lifetime (7 days default)
    - Used to get new access token without re-login
    - Improves UX: user stays logged in for days
    - Still secure: if refresh token is stolen, it expires eventually
    
    Token Refresh Flow:
    1. Access token expires (30 min)
    2. Client detects 401 Unauthorized
    3. Client sends refresh token to /api/v1/auth/refresh
    4. Server validates refresh token
    5. Server issues new access token + new refresh token
    6. Client continues with new tokens
    
    Args:
        data: Dictionary to encode (usually {"sub": user_id})
    
    Returns:
        JWT refresh token string
    """
    to_encode = data.copy()
    
    expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    
    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "refresh"
    })
    
    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )
    
    return encoded_jwt


def decode_token(token: str) -> Dict[str, Any]:
    """
    Decode and verify JWT token
    
    Technical Explanation:
    - Verifies signature using SECRET_KEY
    - Checks if token is expired
    - Returns payload if valid
    - Raises exception if invalid
    
    Args:
        token: JWT token string
    
    Returns:
        Dictionary with token payload
    
    Raises:
        HTTPException: If token is invalid or expired
    """
    try:
        # Decode and verify
        # Technical Note: This checks signature + expiry automatically
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        return payload
    
    except JWTError as e:
        logger.warning(f"JWT decode error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_user_id(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> str:
    """
    FastAPI dependency to get current user from JWT token
    
    Technical Explanation:
    - Extracts token from Authorization header
    - Verifies token
    - Returns user_id from token payload
    - If token invalid, raises 401 Unauthorized
    
    Usage in protected routes:
        @router.get("/profile")
        async def get_profile(
            user_id: str = Depends(get_current_user_id)
        ):
            # user_id is automatically extracted from JWT
            user = await db.users.find_one({"_id": user_id})
            return user
    
    Args:
        credentials: Auto-injected by FastAPI from Authorization header
    
    Returns:
        User ID string
    
    Raises:
        HTTPException: If token is invalid
    """
    token = credentials.credentials
    
    try:
        payload = decode_token(token)
        user_id: str = payload.get("sub")
        
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload",
            )
        
        # Optional: Check if token type is access (not refresh)
        token_type = payload.get("type")
        if token_type != "access":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type",
            )
        
        return user_id
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error extracting user from token: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )


# Optional: Role-based access control helper
def require_role(required_role: str):
    """
    Decorator factory for role-based access control
    
    Technical Note: This is more advanced - not needed for MVP
    But shows how to extend authentication with roles
    
    Usage:
        @router.delete("/products/{id}")
        @require_role("admin")
        async def delete_product(id: str):
            # Only admins can access this
    """
    async def role_checker(user_id: str = Depends(get_current_user_id)):
        # In full implementation:
        # 1. Load user from database
        # 2. Check user.role == required_role
        # 3. Raise 403 Forbidden if not authorized
        # For now, just return user_id
        return user_id
    
    return role_checker
