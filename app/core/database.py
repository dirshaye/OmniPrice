from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient
import logging

from app.core.config import settings
from app.models.product import Product
from app.models.competitor import Competitor
from app.models.pricing import PricingRule, PricingDecision, PriceHistory
from app.models.scraper import ScrapeJob, ScrapingError
from app.models.user import User

logger = logging.getLogger(__name__)

class Database:
    client: AsyncIOMotorClient = None
    database = None

db = Database()

async def get_database():
    return db.database

async def init_db():
    """Initialize database connection and Beanie"""
    try:
        # Create Motor client
        db.client = AsyncIOMotorClient(settings.MONGODB_URL)
        db.database = db.client[settings.MONGODB_DB_NAME]
        
        # Test connection
        await db.client.admin.command('ping')
        logger.info(f"Connected to MongoDB: {settings.MONGODB_DB_NAME}")
        
        # Initialize Beanie with document models
        await init_beanie(
            database=db.database,
            document_models=[
                User,
                Product,
                Competitor,
                PricingRule,
                PricingDecision,
                PriceHistory,
                ScrapeJob,
                ScrapingError,
            ]
        )
        
        logger.info("Beanie initialized with all models")
        
        # Create indexes
        await create_indexes()
        
    except Exception as e:
        logger.error(f"Failed to connect to MongoDB: {e}")
        raise

async def close_db():
    """Close database connection"""
    if db.client:
        db.client.close()
        logger.info("Database connection closed")

async def create_indexes():
    """Create database indexes for better performance"""
    try:
        # Product indexes
        await Product.create_index("sku", unique=True)
        await Product.create_index("category")
        await Product.create_index("is_active")
        
        # Competitor indexes
        await Competitor.create_index("domain", unique=True)
        await Competitor.create_index("is_active")
        
        # Price history indexes
        await PriceHistory.create_index([("product_id", 1), ("timestamp", -1)])
        await PriceHistory.create_index("timestamp")
        
        # Pricing decision indexes
        await PricingDecision.create_index([("product_id", 1), ("timestamp", -1)])
        await PricingDecision.create_index("status")
        
        # Scrape job indexes
        await ScrapeJob.create_index("status")
        await ScrapeJob.create_index("created_at")
        
        # User indexes
        await User.create_index("email", unique=True)
        await User.create_index("username", unique=True)
        
        logger.info("Database indexes created successfully")
        
    except Exception as e:
        logger.warning(f"Error creating indexes: {e}")

# Dependency to get database session
async def get_db():
    return await get_database()
