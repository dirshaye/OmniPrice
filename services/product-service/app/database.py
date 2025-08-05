#!/usr/bin/env python3
"""
Database configuration for Product Service
"""

from datetime import datetime
from typing import List, Optional
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
import logging

# Import local models
from app.models import Product, ProductStatus, PriceHistory, CompetitorData

logger = logging.getLogger(__name__)

# Define models specific to this service
PRODUCT_SERVICE_MODELS = [
    Product,
]

class ProductDatabase:
    """Product service database manager"""
    
    def __init__(self, mongo_uri: str, db_name: str):
        self.mongo_uri = mongo_uri
        self.db_name = db_name
        self.client = None
        self.database = None

    async def connect(self):
        """Connect to MongoDB and initialize Beanie"""
        try:
            print(f"🔄 Connecting to MongoDB...")
            self.client = AsyncIOMotorClient(self.mongo_uri)
            self.database = self.client[self.db_name]
            
            # Test connection
            print(f"🔄 Testing MongoDB connection...")
            await self.client.admin.command('ping')
            print(f"✅ Connected to MongoDB: {self.db_name}")
            logger.info(f"✅ Connected to MongoDB: {self.db_name}")
            
            # Initialize Beanie with product models
            print(f"🔄 Initializing Beanie with models...")
            await init_beanie(
                database=self.database,
                document_models=PRODUCT_SERVICE_MODELS
            )
            
            print(f"✅ Beanie initialized with {len(PRODUCT_SERVICE_MODELS)} models")
            logger.info(f"✅ Beanie initialized with {len(PRODUCT_SERVICE_MODELS)} models")
            
        except Exception as e:
            print(f"❌ Failed to connect to MongoDB: {e}")
            logger.error(f"❌ Failed to connect to MongoDB: {e}")
            raise

    async def disconnect(self):
        """Close database connection"""
        if self.client:
            self.client.close()
            print("🔌 Database connection closed")
            logger.info("🔌 Database connection closed")

    def get_database(self):
        """Get database instance"""
        return self.database

# Global database manager
db_manager: Optional[ProductDatabase] = None

async def init_database(mongo_uri: str, db_name: str):
    """Initialize database for product service"""
    global db_manager
    
    print(f"🔄 Initializing database manager...")
    db_manager = ProductDatabase(mongo_uri, db_name)
    await db_manager.connect()
    return db_manager

async def get_database():
    """Get database instance"""
    if db_manager is None:
        raise RuntimeError("Database not initialized. Call init_database first.")
    return db_manager.get_database()

async def close_database():
    """Close database connection"""
    if db_manager:
        await db_manager.disconnect()
