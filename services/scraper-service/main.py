"""
Scraper Service - Main application entry point
"""

import asyncio
import logging
import signal
from contextlib import asynccontextmanager
from fastapi import FastAPI
import grpc
from concurrent import futures

from app.config import get_settings
from app.database import connect_to_mongo, close_mongo_connection
from app.service import ScraperService
from app.proto import scraper_service_pb2_grpc

settings = get_settings()

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format=settings.LOG_FORMAT
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    logger.info("🚀 Starting Scraper Service...")
    try:
        await connect_to_mongo()
        logger.info("✅ Scraper Service started successfully")
        yield
    except Exception as e:
        logger.error(f"❌ Failed to start service: {e}")
        raise
    finally:
        # Shutdown
        logger.info("🛑 Shutting down Scraper Service...")
        await close_mongo_connection()
        logger.info("✅ Scraper Service shut down complete")

def create_app() -> FastAPI:
    """Create FastAPI application"""
    app = FastAPI(
        title="OmniPriceX Scraper Service",
        description="High-performance web scraping service with Playwright",
        version=settings.SERVICE_VERSION,
        lifespan=lifespan
    )
    
    @app.get("/health")
    async def health_check():
        """Health check endpoint"""
        return {
            "status": "healthy",
            "service": settings.SERVICE_NAME,
            "version": settings.SERVICE_VERSION
        }
    
    @app.get("/")
    async def root():
        """Root endpoint"""
        return {
            "service": settings.SERVICE_NAME,
            "version": settings.SERVICE_VERSION,
            "description": "OmniPriceX Scraper Service with Playwright"
        }
    
    return app

def create_grpc_server():
    """Create gRPC server"""
    server = grpc.aio.server(futures.ThreadPoolExecutor(max_workers=10))
    scraper_service_pb2_grpc.add_ScraperServiceServicer_to_server(
        ScraperService(), 
        server
    )
    listen_addr = f"[::]:{settings.GRPC_PORT}"
    server.add_insecure_port(listen_addr)
    return server

async def serve_grpc():
    """Start gRPC server"""
    server = create_grpc_server()
    
    logger.info(f"🎯 Starting gRPC server on port {settings.GRPC_PORT}")
    await server.start()
    
    # Graceful shutdown
    async def shutdown():
        logger.info("🛑 Stopping gRPC server...")
        await server.stop(5)
        logger.info("✅ gRPC server stopped")
    
    # Wait for server to be stopped
    try:
        await server.wait_for_termination()
    except KeyboardInterrupt:
        await shutdown()

async def main():
    """Main application entry point"""
    # Initialize database connection
    await connect_to_mongo()
    
    # Start gRPC server
    await serve_grpc()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("🛑 Service interrupted by user")
    except Exception as e:
        logger.error(f"❌ Service failed: {e}")
        raise

# FastAPI app instance for development
app = create_app()
