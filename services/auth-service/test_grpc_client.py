#!/usr/bin/env python3
"""
Test client for gRPC Auth Service
"""

import asyncio
import grpc
import logging
import sys

# Add project root to path
sys.path.append('/home/dre/Desktop/Github/OmniPriceX')

from shared.proto import auth_service_pb2
from shared.proto import auth_service_pb2_grpc

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_auth_service():
    """Test the Auth service via gRPC"""
    
    # Connect to the auth server
    async with grpc.aio.insecure_channel('localhost:8001') as channel:
        stub = auth_service_pb2_grpc.AuthServiceStub(channel)
        
        logger.info("🔌 Connected to Auth Service on localhost:8001")
        
        # Test 1: Register User
        logger.info("\n🧪 Test 1: RegisterUser")
        register_request = auth_service_pb2.RegisterUserRequest(
            username="testuser",
            email="test@omnipricex.com",
            password="securepassword123",
            full_name="Test User"
        )
        
        try:
            response = await stub.RegisterUser(register_request)
            if response.success:
                logger.info("✅ RegisterUser - Success")
                logger.info(f"User ID: {response.user.id}")
                logger.info(f"Email: {response.user.email}")
                logger.info(f"Username: {response.user.username}")
            else:
                logger.warning(f"⚠️ RegisterUser - Failed: {response.message}")
        except Exception as e:
            logger.error(f"❌ RegisterUser failed: {e}")
        
        # Test 2: Login User
        logger.info("\n🧪 Test 2: LoginUser")
        login_request = auth_service_pb2.LoginUserRequest(
            email="test@omnipricex.com",
            password="securepassword123"
        )
        
        access_token = None
        refresh_token = None
        
        try:
            response = await stub.LoginUser(login_request)
            if response.access_token:
                logger.info("✅ LoginUser - Success")
                logger.info(f"Access Token: {response.access_token[:20]}...")
                logger.info(f"User: {response.user.username}")
                access_token = response.access_token
                refresh_token = response.refresh_token
            else:
                logger.error("❌ LoginUser - No tokens received")
        except Exception as e:
            logger.error(f"❌ LoginUser failed: {e}")
        
        # Test 3: Verify Token
        if access_token:
            logger.info("\n🧪 Test 3: VerifyToken")
            verify_request = auth_service_pb2.VerifyTokenRequest(
                token=access_token
            )
            
            try:
                response = await stub.VerifyToken(verify_request)
                if response.is_valid:
                    logger.info("✅ VerifyToken - Success")
                    logger.info(f"User ID: {response.user_id}")
                    logger.info(f"Email: {response.email}")
                else:
                    logger.error("❌ VerifyToken - Invalid token")
            except Exception as e:
                logger.error(f"❌ VerifyToken failed: {e}")
        
        # Test 4: Refresh Token
        if refresh_token:
            logger.info("\n🧪 Test 4: RefreshToken")
            refresh_request = auth_service_pb2.RefreshTokenRequest(
                refresh_token=refresh_token
            )
            
            try:
                response = await stub.RefreshToken(refresh_request)
                if response.access_token:
                    logger.info("✅ RefreshToken - Success")
                    logger.info(f"New Access Token: {response.access_token[:20]}...")
                else:
                    logger.error("❌ RefreshToken - No new token received")
            except Exception as e:
                logger.error(f"❌ RefreshToken failed: {e}")

if __name__ == '__main__':
    logger.info("🚀 Starting gRPC Auth Service Test")
    asyncio.run(test_auth_service())
