#!/usr/bin/env python3
"""
Product Service - gRPC server for product management
"""

import asyncio
import logging
import signal
import sys
import os
from concurrent import futures

import grpc

# Add proto directory to path
import sys
import os
current_dir = os.path.dirname(os.path.abspath(__file__))
proto_dir = os.path.join(current_dir, '..', '..', 'shared', 'proto')
proto_dir = os.path.abspath(proto_dir)
sys.path.insert(0, proto_dir)

# Import proto files directly
import product_service_pb2_grpc
from app.config import settings
from app.database import init_database, close_database
from app.service import ProductService

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format=settings.LOG_FORMAT
)
logger = logging.getLogger(__name__)


async def init_services():
    """Initialize all services"""
    try:
        print("🔄 Initializing Product Service...")
        print(f"🔗 Connecting to MongoDB: {settings.MONGO_URI[:50]}...")
        
        # Initialize database
        await init_database(settings.MONGO_URI, settings.MONGO_DB)
        print("✅ Database connected successfully")
        logger.info("✅ Product Service initialized successfully")
        
    except Exception as e:
        print(f"❌ Failed to initialize services: {e}")
        logger.error(f"❌ Failed to initialize services: {e}")
        raise


async def cleanup_services():
    """Cleanup all services"""
    try:
        await close_database()
        logger.info("🔌 Product Service cleanup completed")
    except Exception as e:
        logger.error(f"❌ Error during cleanup: {e}")


def create_grpc_server():
    """Create and configure gRPC server"""
    # Create server with thread pool
    server = grpc.aio.server(futures.ThreadPoolExecutor(max_workers=10))
    
    # Add services
    product_service_pb2_grpc.add_ProductServiceServicer_to_server(
        ProductService(), server
    )
    
    # Configure server address
    listen_addr = f"{settings.HOST}:{settings.GRPC_PORT}"
    server.add_insecure_port(listen_addr)
    
    return server, listen_addr


async def serve():
    """Start the gRPC server"""
    print("🚀 Starting Product Service...")
    
    # Initialize services
    await init_services()
    
    # Create server
    print("🔧 Creating gRPC server...")
    server, listen_addr = create_grpc_server()
    
    # Setup graceful shutdown
    def signal_handler(signum, frame):
        logger.info(f"🛑 Received signal {signum}, shutting down...")
        asyncio.create_task(shutdown(server))
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Start server
    print(f"🚀 Product Service starting on {listen_addr}")
    logger.info(f"🚀 Product Service starting on {listen_addr}")
    logger.info(f"📊 Service: {settings.SERVICE_NAME} v{settings.SERVICE_VERSION}")
    logger.info(f"🗄️  Database: {settings.MONGO_DB}")
    logger.info(f"🔧 Debug mode: {settings.DEBUG}")
    
    print("🔄 Starting gRPC server...")
    await server.start()
    print(f"✅ Product Service running on {listen_addr}")
    logger.info(f"✅ Product Service running on {listen_addr}")
    
    try:
        print("⏳ Waiting for requests (Press Ctrl+C to stop)...")
        await server.wait_for_termination()
    except KeyboardInterrupt:
        print("🛑 Keyboard interrupt received")
        logger.info("🛑 Keyboard interrupt received")
    finally:
        await shutdown(server)


async def shutdown(server):
    """Graceful shutdown"""
    logger.info("🛑 Shutting down Product Service...")
    
    # Stop accepting new requests
    await server.stop(grace=30)
    
    # Cleanup services
    await cleanup_services()
    
    logger.info("✅ Product Service shutdown complete")


def main():
    """Main entry point"""
    try:
        asyncio.run(serve())
    except KeyboardInterrupt:
        logger.info("🛑 Product Service stopped by user")
    except Exception as e:
        logger.error(f"❌ Product Service failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
