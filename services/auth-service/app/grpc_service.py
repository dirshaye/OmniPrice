#!/usr/bin/env python3
"""
gRPC Auth Service Implementation
Replaces REST endpoints with gRPC methods
"""

import grpc
import sys
from datetime import timezone
from typing import Optional
from google.protobuf.timestamp_pb2 import Timestamp

# Add project root to path
sys.path.append('/home/dre/Desktop/Github/OmniPriceX')

from shared.proto import auth_service_pb2
from shared.proto import auth_service_pb2_grpc
from .auth import AuthService as AuthBusinessLogic
from .models import UserCreate, UserLogin
from .config import get_settings

class AuthService(auth_service_pb2_grpc.AuthServiceServicer):
    """gRPC Auth Service Implementation"""
    
    def __init__(self):
        self.settings = get_settings()
        self.auth_logic = AuthBusinessLogic(secret_key=self.settings.SECRET_KEY)
    
    async def RegisterUser(self, request, context):
        """Register a new user"""
        try:
            print(f"DEBUG: RegisterUser called with email={request.email}, username={request.username}")
            
            # Convert gRPC request to business logic model
            user_data = UserCreate(
                email=request.email,
                username=request.username,
                password=request.password,
                full_name=request.full_name,
                company_name=None  # Proto doesn't have this field, set to None
            )
            
            print(f"DEBUG: UserCreate object created: {user_data}")
            
            # Call existing business logic
            user = await self.auth_logic.register_user(user_data)
            
            print(f"DEBUG: User registered successfully: {user.id}")
            
            # Convert to gRPC response
            created_timestamp = Timestamp()
            # Make datetime timezone-aware before converting to protobuf
            created_dt = user.created_at.replace(tzinfo=timezone.utc) if user.created_at.tzinfo is None else user.created_at
            created_timestamp.FromDatetime(created_dt)
            
            updated_timestamp = Timestamp()
            if user.updated_at:
                updated_dt = user.updated_at.replace(tzinfo=timezone.utc) if user.updated_at.tzinfo is None else user.updated_at
                updated_timestamp.FromDatetime(updated_dt)
            
            user_response = auth_service_pb2.User(
                id=str(user.id),
                username=user.username,
                email=user.email,
                full_name=user.full_name,
                is_active=user.is_active,
                is_staff=user.role == "admin",
                created_at=created_timestamp,
                updated_at=updated_timestamp if user.updated_at else created_timestamp
            )
            
            print(f"DEBUG: User response created successfully")
            
            return auth_service_pb2.UserResponse(
                success=True,
                message="User registered successfully",
                user=user_response
            )
            
        except Exception as e:
            print(f"DEBUG: Exception in RegisterUser: {type(e).__name__}: {str(e)}")
            import traceback
            traceback.print_exc()
            
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return auth_service_pb2.UserResponse(
                success=False,
                message=f"Registration failed: {str(e)}"
            )
    
    async def LoginUser(self, request, context):
        """Login user and return tokens"""
        try:
            # Convert gRPC request to business logic model
            login_data = UserLogin(
                email=request.email,
                password=request.password
            )
            
            # Call existing business logic
            tokens = await self.auth_logic.login_user(
                login_data=login_data,
                user_agent="gRPC-Client",  # Could be passed in metadata
                ip_address="internal"      # Could be extracted from context
            )
            
            # Get user info for response
            user = await self.auth_logic.get_current_user(tokens.access_token)
            
            # Convert to gRPC response
            created_timestamp = Timestamp()
            # Make datetime timezone-aware before converting to protobuf
            created_dt = user.created_at.replace(tzinfo=timezone.utc) if user.created_at.tzinfo is None else user.created_at
            created_timestamp.FromDatetime(created_dt)
            
            updated_timestamp = Timestamp()
            if user.updated_at:
                updated_dt = user.updated_at.replace(tzinfo=timezone.utc) if user.updated_at.tzinfo is None else user.updated_at
                updated_timestamp.FromDatetime(updated_dt)
            
            user_response = auth_service_pb2.User(
                id=str(user.id),
                username=user.username,
                email=user.email,
                full_name=user.full_name,
                is_active=user.is_active,
                is_staff=user.role == "admin",
                created_at=created_timestamp,
                updated_at=updated_timestamp if user.updated_at else created_timestamp
            )
            
            return auth_service_pb2.LoginUserResponse(
                access_token=tokens.access_token,
                refresh_token=tokens.refresh_token,
                user=user_response
            )
            
        except Exception as e:
            context.set_code(grpc.StatusCode.UNAUTHENTICATED)
            context.set_details(str(e))
            return auth_service_pb2.LoginUserResponse()
    
    async def VerifyToken(self, request, context):
        """Verify if a token is valid"""
        try:
            # Call existing business logic
            payload = self.auth_logic.verify_token(request.token)
            
            return auth_service_pb2.VerifyTokenResponse(
                is_valid=True,
                user_id=payload.get("sub"),
                email=payload.get("email")
            )
            
        except Exception as e:
            return auth_service_pb2.VerifyTokenResponse(
                is_valid=False,
                user_id="",
                email=""
            )
    
    async def RefreshToken(self, request, context):
        """Refresh access token using refresh token"""
        try:
            # Call existing business logic
            tokens = await self.auth_logic.refresh_access_token(request.refresh_token)
            
            # Get user info
            user = await self.auth_logic.get_current_user(tokens.access_token)
            
            # Convert to gRPC response
            created_timestamp = Timestamp()
            # Make datetime timezone-aware before converting to protobuf
            created_dt = user.created_at.replace(tzinfo=timezone.utc) if user.created_at.tzinfo is None else user.created_at
            created_timestamp.FromDatetime(created_dt)
            
            updated_timestamp = Timestamp()
            if user.updated_at:
                updated_dt = user.updated_at.replace(tzinfo=timezone.utc) if user.updated_at.tzinfo is None else user.updated_at
                updated_timestamp.FromDatetime(updated_dt)
            
            user_response = auth_service_pb2.User(
                id=str(user.id),
                username=user.username,
                email=user.email,
                full_name=user.full_name,
                is_active=user.is_active,
                is_staff=user.role == "admin",
                created_at=created_timestamp,
                updated_at=updated_timestamp if user.updated_at else created_timestamp
            )
            
            return auth_service_pb2.LoginUserResponse(
                access_token=tokens.access_token,
                refresh_token=tokens.refresh_token,
                user=user_response
            )
            
        except Exception as e:
            context.set_code(grpc.StatusCode.UNAUTHENTICATED)
            context.set_details(str(e))
            return auth_service_pb2.LoginUserResponse()
    
    async def LogoutUser(self, request, context):
        """Logout user by user ID (Note: proto expects user_id, not refresh_token)"""
        try:
            # For now, we'll need to adapt this to work with user_id
            # In a real implementation, you might need to revoke all tokens for a user
            # or modify the proto to accept refresh_token instead
            
            # This is a placeholder - you'd need to implement user-based logout
            # For now, just return success
            from google.protobuf.empty_pb2 import Empty
            return Empty()
            
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            from google.protobuf.empty_pb2 import Empty
            return Empty()
    
    async def GetUserProfile(self, request, context):
        """Get user profile by user ID"""
        try:
            # Note: This would need a new method in auth business logic
            # to get user by ID rather than by token
            # For now, this is a placeholder implementation
            
            context.set_code(grpc.StatusCode.UNIMPLEMENTED)
            context.set_details("GetUserProfile by user_id not yet implemented")
            return auth_service_pb2.UserResponse(
                success=False,
                message="Feature requires implementation of get_user_by_id method"
            )
            
        except Exception as e:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details(str(e))
            return auth_service_pb2.UserResponse(
                success=False,
                message=f"User not found: {str(e)}"
            )
    
    async def UpdateUserProfile(self, request, context):
        """Update user profile (placeholder for future implementation)"""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details("UpdateUserProfile not yet implemented")
        return auth_service_pb2.UserResponse(
            success=False,
            message="Feature not implemented yet"
        )
