"""
Database connection and models for scraper service
"""

import asyncio
import logging
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from .models import ScrapeJob, ScrapeHistory
from .config import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)

# Global database client
mongo_client = None

async def connect_to_mongo():
    """Create database connection"""
    global mongo_client
    
    try:
        mongo_client = AsyncIOMotorClient(
            settings.MONGODB_URL,
            serverSelectionTimeoutMS=5000
        )
        
        # Test the connection
        await mongo_client.admin.command('ping')
        logger.info("🟢 Connected to MongoDB successfully")
        
        # Initialize Beanie with the models
        await init_beanie(
            database=mongo_client[settings.DATABASE_NAME],
            document_models=[ScrapeJob, ScrapeHistory]
        )
        
        logger.info("🟢 Beanie initialized with models")
        
    except Exception as e:
        logger.error(f"❌ Failed to connect to MongoDB: {e}")
        raise e

async def close_mongo_connection():
    """Close database connection"""
    global mongo_client
    
    if mongo_client:
        mongo_client.close()
        logger.info("🔴 MongoDB connection closed")

# Re-export models for backward compatibility
from .models import ScrapeJob, ScrapeHistory
