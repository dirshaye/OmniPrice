"""
Pricing Service - Main Application Entry Point
"""

import asyncio
import logging
import signal
import sys
import os

# Add project root to path
sys.path.append('/home/dre/Desktop/Github/OmniPriceX')

import grpc
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie

from app.config import settings
from app.database import PricingRule, PricingDecision, PriceHistory
from app.service import PricingService
from shared.proto import pricing_service_pb2_grpc

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class PricingServiceServer:
    """Pricing Service gRPC Server"""
    
    def __init__(self):
        self.server = None
        self.mongodb_client = None
        logger.info("🎯 Initializing Pricing Service Server")
    
    async def init_database(self):
        """Initialize MongoDB connection and Beanie"""
        try:
            logger.info(f"🔌 Connecting to MongoDB: {settings.MONGO_URI}")
            
            # Create MongoDB client
            self.mongodb_client = AsyncIOMotorClient(settings.MONGO_URI)
            
            # Test connection
            await self.mongodb_client.admin.command('ping')
            logger.info("✅ MongoDB connection successful")
            
            # Initialize Beanie with document models
            database = self.mongodb_client[settings.MONGO_DB]
            await init_beanie(
                database=database,
                document_models=[
                    PricingRule,
                    PricingDecision,
                    PriceHistory
                ]
            )
            
            logger.info(f"✅ Database '{settings.MONGO_DB}' initialized with Beanie")
            
            # Create indexes
            await self._create_indexes()
            
        except Exception as e:
            logger.error(f"❌ Database initialization failed: {e}")
            raise
    
    async def _create_indexes(self):
        """Create database indexes for better performance"""
        try:
            # These are already defined in the Document classes, but we can create additional ones
            logger.info("📊 Creating database indexes...")
            
            # Additional composite indexes for common queries
            await PricingDecision.get_motor_collection().create_index([
                ("product_id", 1),
                ("status", 1),
                ("timestamp", -1)
            ], background=True)
            
            await PriceHistory.get_motor_collection().create_index([
                ("product_id", 1),
                ("competitor_id", 1),
                ("timestamp", -1)
            ], background=True)
            
            logger.info("✅ Database indexes created")
            
        except Exception as e:
            logger.warning(f"⚠️ Index creation warning: {e}")
    
    async def start_server(self):
        """Start the gRPC server"""
        try:
            # Initialize database first
            await self.init_database()
            
            # Create gRPC server
            self.server = grpc.aio.server()
            
            # Add service to server
            pricing_service = PricingService()
            pricing_service_pb2_grpc.add_PricingServiceServicer_to_server(
                pricing_service, self.server
            )
            
            # Configure server address
            listen_addr = f'[::]:{settings.GRPC_PORT}'
            self.server.add_insecure_port(listen_addr)
            
            # Start server
            logger.info(f"🚀 Starting Pricing Service gRPC server on {listen_addr}")
            await self.server.start()
            
            logger.info("✅ Pricing Service is ready to accept requests!")
            logger.info(f"🎯 Service: {settings.SERVICE_NAME} v{settings.VERSION}")
            logger.info(f"📡 gRPC Port: {settings.GRPC_PORT}")
            logger.info(f"🗄️ Database: {settings.MONGO_DB}")
            
            # Wait for termination
            await self.server.wait_for_termination()
            
        except Exception as e:
            logger.error(f"❌ Server startup failed: {e}")
            raise
    
    async def stop_server(self):
        """Gracefully stop the server"""
        logger.info("🛑 Shutting down Pricing Service...")
        
        if self.server:
            # Stop accepting new requests and wait for existing ones to complete
            await self.server.stop(grace=5.0)
            logger.info("✅ gRPC server stopped")
        
        if self.mongodb_client:
            self.mongodb_client.close()
            logger.info("✅ MongoDB connection closed")

# Global server instance
pricing_server = PricingServiceServer()

async def main():
    """Main async function"""
    
    def signal_handler(signum, frame):
        """Handle shutdown signals"""
        logger.info(f"📶 Received signal {signum}")
        # Create a task to stop the server gracefully
        loop = asyncio.get_event_loop()
        loop.create_task(pricing_server.stop_server())
    
    # Register signal handlers
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)
    
    try:
        await pricing_server.start_server()
    except KeyboardInterrupt:
        logger.info("🛑 Keyboard interrupt received")
    except Exception as e:
        logger.error(f"❌ Server error: {e}")
        sys.exit(1)
    finally:
        await pricing_server.stop_server()

if __name__ == "__main__":
    logger.info("🎯 Starting OmniPriceX Pricing Service")
    logger.info("=" * 50)
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("🛑 Service interrupted by user")
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}")
        sys.exit(1)
