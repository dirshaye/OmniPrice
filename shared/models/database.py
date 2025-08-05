from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient
import logging
from typing import List, Type
from beanie import Document

logger = logging.getLogger(__name__)

class DatabaseManager:
    """Shared database manager for all microservices"""
    
    def __init__(self, mongodb_url: str, db_name: str):
        self.mongodb_url = mongodb_url
        self.db_name = db_name
        self.client: AsyncIOMotorClient = None
        self.database = None
    
    async def connect(self, document_models: List[Type[Document]]):
        """Connect to MongoDB and initialize Beanie"""
        try:
            # Create Motor client
            self.client = AsyncIOMotorClient(self.mongodb_url)
            self.database = self.client[self.db_name]
            
            # Test connection
            await self.client.admin.command('ping')
            logger.info(f"Connected to MongoDB: {self.db_name}")
            
            # Initialize Beanie with document models
            await init_beanie(
                database=self.database,
                document_models=document_models
            )
            
            logger.info(f"Beanie initialized with {len(document_models)} models")
            
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise
    
    async def disconnect(self):
        """Close database connection"""
        if self.client:
            self.client.close()
            logger.info("Database connection closed")
    
    def get_database(self):
        """Get database instance"""
        return self.database

# Import all models that will be shared across services
def get_all_models():
    """Get all document models for database initialization"""
    from app.models.user import User
    from app.models.product import Product
    from app.models.competitor import Competitor
    from app.models.pricing import PricingRule, PricingDecision, PriceHistory
    from app.models.scraper import ScrapeJob, ScrapingError, ScrapedData
    
    return [
        User,
        Product,
        Competitor,
        PricingRule,
        PricingDecision,
        PriceHistory,
        ScrapeJob,
        ScrapingError,
        ScrapedData,
    ]

# Global database manager instance
db_manager = None

async def init_database(mongodb_url: str, db_name: str, models: List[Type[Document]] = None):
    """Initialize database for a service"""
    global db_manager
    
    if models is None:
        models = get_all_models()
    
    db_manager = DatabaseManager(mongodb_url, db_name)
    await db_manager.connect(models)
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
