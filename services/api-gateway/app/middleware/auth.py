from fastapi import Request, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from starlette.middleware.base import BaseHTTPMiddleware
from jose import JWTError, jwt
from typing import Optional
import logging

from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()
security = HTTPBearer()


class AuthMiddleware(BaseHTTPMiddleware):
    """Authentication middleware for protecting routes"""
    
    # Routes that don't require authentication
    EXCLUDED_PATHS = {
        "/",
        "/health",
        "/api/v1",
        "/api/v1/docs",
        "/api/v1/redoc", 
        "/api/v1/openapi.json",
        "/api/v1/auth/login",
        "/api/v1/auth/register",
        "/api/v1/auth/refresh"
    }
    
    async def dispatch(self, request: Request, call_next):
        """Process the request and check authentication"""
        
        # Skip auth for excluded paths
        if request.url.path in self.EXCLUDED_PATHS:
            return await call_next(request)
        
        # Skip auth for OPTIONS requests (CORS preflight)
        if request.method == "OPTIONS":
            return await call_next(request)
        
        try:
            # Extract token from Authorization header
            authorization: str = request.headers.get("Authorization")
            if not authorization:
                raise HTTPException(
                    status_code=401,
                    detail="Authorization header missing"
                )
            
            # Verify Bearer token format
            if not authorization.startswith("Bearer "):
                raise HTTPException(
                    status_code=401,
                    detail="Invalid authorization header format"
                )
            
            token = authorization.split(" ")[1]
            
            # Decode and verify JWT token
            payload = jwt.decode(
                token,
                settings.JWT_SECRET_KEY,
                algorithms=[settings.JWT_ALGORITHM]
            )
            
            # Extract user info from token
            user_id: str = payload.get("sub")
            if user_id is None:
                raise HTTPException(
                    status_code=401,
                    detail="Invalid token payload"
                )
            
            # Add user info to request state
            request.state.user_id = user_id
            request.state.user_email = payload.get("email")
            
            logger.debug(f"Authenticated user: {user_id}")
            
        except JWTError as e:
            logger.warning(f"JWT decode error: {e}")
            raise HTTPException(
                status_code=401,
                detail="Invalid or expired token"
            )
        except Exception as e:
            logger.error(f"Authentication error: {e}")
            raise HTTPException(
                status_code=401,
                detail="Authentication failed"
            )
        
        response = await call_next(request)
        return response


def get_current_user(request: Request) -> Optional[str]:
    """Extract current user ID from request state"""
    return getattr(request.state, "user_id", None)


def get_current_user_email(request: Request) -> Optional[str]:
    """Extract current user email from request state"""
    return getattr(request.state, "user_email", None)
