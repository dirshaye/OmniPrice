"""
MongoDB Database Connection Module

Technical Explanation:
- Motor is an async MongoDB driver (works with asyncio/FastAPI)
- We create a single database connection when app starts
- Connection is reused across all requests (connection pooling)
- This prevents opening/closing connections repeatedly (performance!)
"""

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from beanie import init_beanie
import logging
from typing import Optional
from pymongo.errors import ConnectionFailure

from omniprice.core.config import settings

# Import all models here to register them with Beanie
# We will add models to this list as we create them
from omniprice.modules.auth.models import User
# from omniprice.modules.product.models import Product

logger = logging.getLogger(__name__)

async def init_db():
    """
    Initialize database connection and Beanie ODM
    
    Technical Explanation:
    1. Creates AsyncIOMotorClient (non-blocking MongoDB driver)
    2. Selects the specific database
    3. Initializes Beanie with the database and list of document models
    """
    try:
        client = AsyncIOMotorClient(settings.MONGODB_URL)
        database = client[settings.MONGODB_DB_NAME]
        
        # Initialize Beanie with the database and document models
        # We will uncomment models as we implement them
        await init_beanie(
            database=database,
            document_models=[
                User,
                # Product,
            ]
        )
        
        logger.info("✅ Database connection established successfully")
        
    except Exception as e:
        logger.error(f"❌ Database connection failed: {e}")
        raise e
# Technical Note: These are module-level variables (singletons)
_mongo_client: Optional[AsyncIOMotorClient] = None
_database: Optional[AsyncIOMotorDatabase] = None


async def connect_to_mongodb():
    """
    Establish connection to MongoDB
    
    Technical Flow:
    1. Create AsyncIOMotorClient with connection string
    2. Ping database to verify connection works
    3. Store client globally for reuse
    
    Called once when FastAPI app starts (in main.py startup event)
    """
    global _mongo_client, _database
    
    try:
        logger.info(f"🔌 Connecting to MongoDB at {settings.MONGODB_URL}")
        
        # Create MongoDB client
        # Technical Note: maxPoolSize controls max concurrent connections
        _mongo_client = AsyncIOMotorClient(
            settings.MONGODB_URL,
            maxPoolSize=10,
            minPoolSize=1,
        )
        
        # Get database reference
        _database = _mongo_client[settings.MONGODB_DB_NAME]
        
        # Verify connection by pinging
        await _database.command("ping")
        
        logger.info(f"✅ Connected to MongoDB database: {settings.MONGODB_DB_NAME}")
        
    except ConnectionFailure as e:
        logger.error(f"❌ Failed to connect to MongoDB: {e}")
        raise
    except Exception as e:
        logger.error(f"❌ Unexpected error connecting to MongoDB: {e}")
        raise


async def close_mongodb_connection():
    """
    Close MongoDB connection
    
    Called when FastAPI app shuts down (in main.py shutdown event)
    """
    global _mongo_client
    
    if _mongo_client:
        logger.info("🔌 Closing MongoDB connection...")
        _mongo_client.close()
        logger.info("✅ MongoDB connection closed")


def get_database() -> AsyncIOMotorDatabase:
    """
    Get MongoDB database instance
    
    Usage in repository:
    db = get_database()
    products = db["products"]  # Get collection
    await products.find_one({"_id": product_id})
    
    Technical Note: This is a dependency injection helper
    FastAPI will call this and inject the database into route handlers
    """
    if _database is None:
        raise RuntimeError(
            "Database not initialized. "
            "Did you forget to call connect_to_mongodb() on startup?"
        )
    return _database


def get_collection(collection_name: str):
    """
    Get a specific MongoDB collection
    
    Usage:
    products_collection = get_collection("products")
    await products_collection.insert_one({"name": "iPhone", "price": 999})
    
    Args:
        collection_name: Name of the collection (like a table in SQL)
    
    Returns:
        AsyncIOMotorCollection object for database operations
    """
    db = get_database()
    return db[collection_name]


# Collection name constants
# Technical Note: Using constants prevents typos and makes refactoring easier
class Collections:
    """MongoDB collection names"""
    PRODUCTS = "products"
    PRICING_RULES = "pricing_rules"
    PRICE_HISTORY = "price_history"
    COMPETITORS = "competitors"
    SCRAPE_JOBS = "scrape_jobs"
    USERS = "users"
    MARKET_PRICES = "market_prices"
