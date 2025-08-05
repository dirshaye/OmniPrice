"""
OmniPriceX API Gateway
Main entry point for the microservices platform REST API.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
import os

from app.grpc_clients import GrpcClients
from app.routers.product_router import router as product_router
from app.routers.pricing_router import router as pricing_router 
from app.routers.auth_router import router as auth_router
from app.routers.scheduler_router import router as scheduler_router
from app.routers.llm_router import router as llm_router
from app.middleware.auth import AuthMiddleware
from app.config import get_settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get settings
settings = get_settings()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Initialize gRPC clients
    app.state.grpc_clients = GrpcClients()
    logger.info("API Gateway started successfully")
    
    yield
    
    # Cleanup
    await app.state.grpc_clients.close()
    logger.info("API Gateway shutdown complete")

# Create FastAPI application
app = FastAPI(
    title="OmniPriceX API Gateway",
    description="REST API Gateway for the OmniPriceX microservices platform",
    version="1.0.0",
    openapi_url="/api/v1/openapi.json",
    docs_url="/api/v1/docs",
    redoc_url="/api/v1/redoc",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure based on environment
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add authentication middleware
security = HTTPBearer()
app.add_middleware(AuthMiddleware)

# Include routers
app.include_router(auth_router, prefix="/api/v1")
app.include_router(product_router, prefix="/api/v1")
app.include_router(pricing_router, prefix="/api/v1")
app.include_router(scheduler_router, prefix="/api/v1")
app.include_router(llm_router, prefix="/api/v1")

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint - API Gateway information"""
    return {
        "service": "OmniPriceX API Gateway",
        "version": "1.0.0",
        "status": "running",
        "docs": "/api/v1/docs",
        "services": {
            "auth": "Authentication and user management",
            "products": "Product catalog management",
            "pricing": "AI-powered pricing engine", 
            "scheduler": "Job scheduling and automation",
            "llm": "AI assistant and analysis"
        }
    }

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint for load balancers and monitoring"""
    try:
        # Check gRPC connections health
        grpc_status = await app.state.grpc_clients.health_check()
        return {
            "status": "healthy",
            "service": "api-gateway",
            "version": "1.0.0",
            "services": grpc_status
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail="Service unhealthy")

# API version info
@app.get("/api/v1")
async def api_info():
    """API version information"""
    return {
        "version": "1.0.0",
        "endpoints": {
            "auth": "/api/v1/auth",
            "products": "/api/v1/products",
            "pricing": "/api/v1/pricing",
            "scheduler": "/api/v1/scheduler",
            "llm": "/api/v1/llm"
        }
    }
