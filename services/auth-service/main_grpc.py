#!/usr/bin/env python3
"""
gRPC Auth Service Server
Replaces FastAPI REST server with gRPC server
"""

import asyncio
import grpc
import logging
import sys
from concurrent import futures
from contextlib import asynccontextmanager
import motor.motor_asyncio
from beanie import init_beanie

# Add project root to path
sys.path.append('/home/dre/Desktop/Github/OmniPriceX')

from shared.proto import auth_service_pb2_grpc
from app.grpc_service import AuthService
from app.config import get_settings
from app.models import User, RefreshToken

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get settings
settings = get_settings()

async def init_database():
    """Initialize MongoDB connection and Beanie"""
    try:
        # Initialize MongoDB connection
        client = motor.motor_asyncio.AsyncIOMotorClient(settings.MONGODB_URL)
        database = client[settings.DATABASE_NAME]
        
        # Initialize Beanie with document models
        await init_beanie(database=database, document_models=[User, RefreshToken])
        
        logger.info(f"🚀 {settings.PROJECT_NAME} started successfully!")
        logger.info(f"📊 Database: {settings.DATABASE_NAME}")
        logger.info(f"🌍 Environment: {settings.ENVIRONMENT}")
        
        return client
        
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")
        raise

async def serve():
    """Start the gRPC server"""
    # Initialize database first
    db_client = await init_database()
    
    try:
        # Create gRPC server
        server = grpc.aio.server(futures.ThreadPoolExecutor(max_workers=10))
        
        # Add the Auth service
        auth_service_pb2_grpc.add_AuthServiceServicer_to_server(
            AuthService(), server
        )
        
        # Listen on port 8001 (same as before)
        listen_addr = '[::]:8001'
        server.add_insecure_port(listen_addr)
        
        logger.info(f"🚀 Starting gRPC Auth Service on {listen_addr}")
        logger.info(f"📡 Protocol: gRPC (instead of REST)")
        logger.info(f"🔐 Services: RegisterUser, LoginUser, VerifyToken, RefreshToken")
        
        # Start the server
        await server.start()
        
        try:
            await server.wait_for_termination()
        except KeyboardInterrupt:
            logger.info("🛑 Shutting down server...")
            await server.stop(5)
            
    except Exception as e:
        logger.error(f"❌ Server startup failed: {e}")
        raise
        
    finally:
        # Cleanup database connection
        if db_client:
            db_client.close()
            logger.info("📴 Auth service shutdown complete")

if __name__ == '__main__':
    logger.info("🔄 Converting Auth Service: REST → gRPC")
    asyncio.run(serve())
