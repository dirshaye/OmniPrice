#!/usr/bin/env python3
"""
Development runner for Auth Service
"""
import uvicorn
import os
from app.config import get_settings

def main():
    """Run the auth service in development mode"""
    settings = get_settings()
    
    print(f"🚀 Starting {settings.PROJECT_NAME}")
    print(f"📍 Environment: {settings.ENVIRONMENT}")
    print(f"🌐 CORS Origins: {settings.BACKEND_CORS_ORIGINS}")
    print(f"📊 Database: {settings.DATABASE_NAME}")
    print(f"🔑 JWT Algorithm: {settings.ALGORITHM}")
    print("=" * 50)
    
    # Run with uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8001,  # Auth service port
        reload=True if settings.ENVIRONMENT == "development" else False,
        log_level="info",
        access_log=True
    )

if __name__ == "__main__":
    main()
