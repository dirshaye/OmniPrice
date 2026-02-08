"""
OmniPrice FastAPI Application Entry Point

Technical Explanation:
- This file creates and configures the FastAPI application
- Handles startup/shutdown events (database connections)
- Registers all API routes
- Sets up middleware (CORS, error handling)
- Configures logging

Startup Flow:
1. Load configuration from .env
2. Connect to MongoDB
3. Register API routes
4. Start Uvicorn server
"""

from fastapi import Depends, FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging
import sys

from omniprice.core.config import settings
from omniprice.core.database import init_db
from omniprice.core.security import get_current_user_id
from omniprice.api.v1.endpoints import analytics
from omniprice.api.v1.endpoints import auth
from omniprice.api.v1.endpoints import competitors
from omniprice.api.v1.endpoints import llm
from omniprice.api.v1.endpoints import pricing
from omniprice.api.v1.endpoints import products
from omniprice.api.v1.endpoints import scraper
from omniprice.core.exceptions import OmniPriceException, exception_to_http_response

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for FastAPI
    Handles startup and shutdown events
    """
    # Startup: Connect to DB
    logger.info("Starting OmniPrice API...")
    await init_db()
    
    yield
    
    # Shutdown: Cleanup
    logger.info("Shutting down OmniPrice API...")


# Create FastAPI application
# Technical Note: lifespan parameter manages startup/shutdown
app = FastAPI(
    title=settings.APP_NAME,
    description="AI-powered dynamic pricing intelligence platform",
    version=settings.APP_VERSION,
    docs_url="/docs",  # Swagger UI at /docs
    redoc_url="/redoc",  # ReDoc UI at /redoc
    lifespan=lifespan,
    debug=settings.DEBUG,
)

# CORS Middleware
# Technical Explanation:
# - CORS = Cross-Origin Resource Sharing
# - Browsers block requests from different domains by default
# - This middleware allows frontend (localhost:3000) to call API (localhost:8000)
# - In production, set CORS_ORIGINS to your actual frontend domain
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],  # Allow all headers
)


# Exception Handlers
# Technical Explanation:
# - FastAPI catches exceptions and returns proper HTTP responses
# - Custom exception handler for our OmniPriceException classes
# - Returns consistent error format across the API

@app.exception_handler(OmniPriceException)
async def omniprice_exception_handler(request: Request, exc: OmniPriceException):
    """
    Handle custom OmniPrice exceptions
    
    Technical Note:
    - Converts our custom exceptions to HTTP responses
    - Returns JSON with error details
    - Includes proper status code (404, 400, 401, etc.)
    """
    logger.warning(f"OmniPrice exception: {exc.message}")
    raise exception_to_http_response(exc)


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """
    Handle unexpected exceptions
    
    Technical Note:
    - Catches any unhandled exception
    - Prevents app crash and returns 500 Internal Server Error
    - Logs full error for debugging
    - In production, don't expose error details to clients (security!)
    """
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    
    # In production, don't expose internal error details
    error_detail = str(exc) if settings.DEBUG else "Internal server error"
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": error_detail,
            "type": "internal_error"
        }
    )


# Root endpoint
@app.get("/", tags=["Health"])
async def root():
    """
    Root endpoint - basic health check
    
    Returns:
        JSON with application info
    """
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
        "environment": settings.ENVIRONMENT,
        "docs": "/docs",
    }


# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check():
    """
    Health check endpoint
    
    Technical Note:
    - Used by load balancers to check if app is healthy
    - Should return 200 OK if app is working
    - Can check database connectivity, etc.
    
    Returns:
        JSON with health status
    """
    # TODO: Add database connectivity check
    
    return {
        "status": "healthy",
        "timestamp": "2025-12-01T00:00:00Z",  # Replace with actual timestamp
    }


# Register Routers
protected_dependencies = [Depends(get_current_user_id)]

app.include_router(auth.router, prefix=f"{settings.API_V1_PREFIX}/auth", tags=["Authentication"])
app.include_router(
    competitors.router,
    prefix=f"{settings.API_V1_PREFIX}/competitors",
    tags=["Competitors"],
    dependencies=protected_dependencies,
)
app.include_router(
    llm.router,
    prefix=f"{settings.API_V1_PREFIX}/llm",
    tags=["LLM"],
    dependencies=protected_dependencies,
)
app.include_router(
    products.router,
    prefix=f"{settings.API_V1_PREFIX}/products",
    tags=["Products"],
    dependencies=protected_dependencies,
)
app.include_router(
    pricing.router,
    prefix=f"{settings.API_V1_PREFIX}/pricing",
    tags=["Pricing"],
    dependencies=protected_dependencies,
)
app.include_router(
    analytics.router,
    prefix=f"{settings.API_V1_PREFIX}/analytics",
    tags=["Analytics"],
    dependencies=protected_dependencies,
)
app.include_router(
    scraper.router,
    prefix=f"{settings.API_V1_PREFIX}/scraper",
    tags=["Scraper"],
    dependencies=protected_dependencies,
)


if __name__ == "__main__":
    """
    Development server entry point
    
    Technical Note:
    - This runs only if you execute: python -m omniprice.main
    - For production, use uvicorn directly: uvicorn omniprice.main:app
    - reload=True watches for code changes and restarts server
    """
    import uvicorn
    
    logger.info(f"🚀 Starting development server on {settings.HOST}:{settings.PORT}")
    
    uvicorn.run(
        "omniprice.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,  # Auto-reload on code changes in debug mode
        log_level=settings.LOG_LEVEL.lower(),
    )
