from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from beanie import init_beanie
import motor.motor_asyncio

from app.config import get_settings
from app.models import User, RefreshToken
from app.routers import auth

# Get settings
settings = get_settings()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager
    Initialize database connections and cleanup on shutdown
    """
    # Initialize MongoDB connection
    client = motor.motor_asyncio.AsyncIOMotorClient(settings.MONGODB_URL)
    database = client[settings.DATABASE_NAME]
    
    # Initialize Beanie with document models
    await init_beanie(database=database, document_models=[User, RefreshToken])
    
    print(f"🚀 {settings.PROJECT_NAME} started successfully!")
    print(f"📊 Database: {settings.DATABASE_NAME}")
    print(f"🌍 Environment: {settings.ENVIRONMENT}")
    
    yield
    
    # Cleanup on shutdown
    client.close()
    print("📴 Auth service shutdown complete")

# Create FastAPI application
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description=settings.DESCRIPTION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url=f"{settings.API_V1_STR}/docs",
    redoc_url=f"{settings.API_V1_STR}/redoc",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix=settings.API_V1_STR)

# Root endpoint
@app.get("/")
async def root():
    """
    Root endpoint - Service information
    """
    return {
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "status": "running",
        "docs": f"{settings.API_V1_STR}/docs"
    }

# Health check endpoint
@app.get("/health")
async def health_check():
    """
    Health check endpoint for load balancers and monitoring
    """
    return {
        "status": "healthy",
        "service": "auth-service",
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT
    }
