"""
Redis Cache Module

Technical Explanation:
- Redis is an in-memory data store (super fast!)
- Used for caching frequently accessed data
- Reduces database load and improves response times
- Example: Cache product details so we don't query MongoDB every time
"""

import redis.asyncio as redis
from typing import Optional, Any
import json
import logging

from omniprice.core.config import settings

logger = logging.getLogger(__name__)

# Global Redis client
# Technical Note: We maintain one connection pool for all requests
_redis_client: Optional[redis.Redis] = None


async def connect_to_redis():
    """
    Establish connection to Redis
    
    Technical Flow:
    1. Create Redis client with connection details
    2. Ping to verify connection
    3. Store globally for reuse
    
    Called when FastAPI app starts
    """
    global _redis_client
    
    try:
        logger.info(f"🔌 Connecting to Redis at {settings.REDIS_HOST}:{settings.REDIS_PORT}")
        
        # Create Redis client
        # Technical Note: decode_responses=True converts bytes to strings automatically
        _redis_client = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=settings.REDIS_DB,
            password=settings.REDIS_PASSWORD,
            decode_responses=True,  # Convert bytes to str
            encoding="utf-8",
            socket_connect_timeout=5,
        )
        
        # Verify connection
        await _redis_client.ping()
        
        logger.info("✅ Connected to Redis successfully")
        
    except Exception as e:
        logger.error(f"❌ Failed to connect to Redis: {e}")
        logger.warning("⚠️ App will continue without cache functionality")
        _redis_client = None


async def close_redis_connection():
    """Close Redis connection"""
    global _redis_client
    
    if _redis_client:
        logger.info("🔌 Closing Redis connection...")
        await _redis_client.close()
        logger.info("✅ Redis connection closed")


def get_redis_client() -> Optional[redis.Redis]:
    """
    Get Redis client instance
    
    Returns None if Redis is not connected (graceful degradation)
    """
    return _redis_client


class CacheService:
    """
    Cache service wrapper for common operations
    
    Technical Explanation:
    - Provides easy-to-use methods for caching
    - Handles serialization (converting Python objects to strings)
    - Automatically handles cache misses
    """
    
    def __init__(self):
        self.client = get_redis_client()
    
    async def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache
        
        Args:
            key: Cache key (e.g., "product:123")
        
        Returns:
            Cached value (auto-deserialized from JSON) or None if not found
        
        Usage:
            cache = CacheService()
            product = await cache.get("product:123")
            if product:
                return product  # Cache hit!
            else:
                # Cache miss - fetch from database
        """
        if not self.client:
            return None
        
        try:
            value = await self.client.get(key)
            if value:
                # Deserialize JSON string back to Python object
                return json.loads(value)
            return None
        except Exception as e:
            logger.error(f"❌ Cache get error for key {key}: {e}")
            return None
    
    async def set(
        self, 
        key: str, 
        value: Any, 
        expire_seconds: int = 300
    ) -> bool:
        """
        Set value in cache
        
        Args:
            key: Cache key
            value: Value to cache (will be JSON serialized)
            expire_seconds: TTL (Time To Live) in seconds (default: 5 minutes)
        
        Returns:
            True if successful, False otherwise
        
        Technical Note:
        - expire_seconds ensures cache doesn't grow indefinitely
        - Old/stale data is automatically removed
        
        Usage:
            cache = CacheService()
            await cache.set("product:123", product_data, expire_seconds=600)
        """
        if not self.client:
            return False
        
        try:
            # Serialize Python object to JSON string
            value_str = json.dumps(value, default=str)  # default=str handles datetime
            await self.client.setex(key, expire_seconds, value_str)
            return True
        except Exception as e:
            logger.error(f"❌ Cache set error for key {key}: {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """
        Delete value from cache
        
        Usage:
            cache = CacheService()
            await cache.delete("product:123")  # Invalidate cached product
        """
        if not self.client:
            return False
        
        try:
            await self.client.delete(key)
            return True
        except Exception as e:
            logger.error(f"❌ Cache delete error for key {key}: {e}")
            return False
    
    async def clear_pattern(self, pattern: str) -> int:
        """
        Delete all keys matching a pattern
        
        Args:
            pattern: Redis pattern (e.g., "product:*" deletes all product caches)
        
        Returns:
            Number of keys deleted
        
        Technical Note:
        - Uses SCAN for memory-efficient iteration (doesn't block Redis)
        - Better than KEYS which can freeze Redis on large datasets
        
        Usage:
            cache = CacheService()
            await cache.clear_pattern("product:*")  # Clear all product caches
        """
        if not self.client:
            return 0
        
        try:
            count = 0
            async for key in self.client.scan_iter(pattern):
                await self.client.delete(key)
                count += 1
            return count
        except Exception as e:
            logger.error(f"❌ Cache clear pattern error for {pattern}: {e}")
            return 0
    
    async def exists(self, key: str) -> bool:
        """Check if key exists in cache"""
        if not self.client:
            return False
        
        try:
            return await self.client.exists(key) > 0
        except Exception as e:
            logger.error(f"❌ Cache exists error for key {key}: {e}")
            return False


# Helper function to get cache service
def get_cache_service() -> CacheService:
    """
    Get CacheService instance
    
    Usage in FastAPI route:
    from fastapi import Depends
    
    @router.get("/products/{product_id}")
    async def get_product(
        product_id: str,
        cache: CacheService = Depends(get_cache_service)
    ):
        # Try cache first
        cached_product = await cache.get(f"product:{product_id}")
        if cached_product:
            return cached_product
        
        # Cache miss - fetch from database
        product = await db.fetch_product(product_id)
        
        # Store in cache for next time
        await cache.set(f"product:{product_id}", product)
        
        return product
    """
    return CacheService()
