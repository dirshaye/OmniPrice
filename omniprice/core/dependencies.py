"""
FastAPI Dependency Injection Helpers

Technical Explanation:
- FastAPI's Depends() system for injecting dependencies
- Instead of creating objects in every route, we inject them
- Makes testing easier (can mock dependencies)
- Ensures consistent object lifecycle
"""

from fastapi import Depends
from typing import Annotated

from omniprice.core.database import get_database
from omniprice.core.cache import get_cache_service, CacheService
from omniprice.core.security import get_current_user_id
from omniprice.core.config import get_settings, Settings


# Database dependency
# Technical Note: Annotated[Type, Depends(func)] is FastAPI's way of dependency injection
DatabaseDep = Annotated[any, Depends(get_database)]

# Cache dependency
CacheDep = Annotated[CacheService, Depends(get_cache_service)]

# Settings dependency
SettingsDep = Annotated[Settings, Depends(get_settings)]

# Current user dependency (for protected routes)
CurrentUserDep = Annotated[str, Depends(get_current_user_id)]


"""
Usage Examples:

1. Protected Route (requires authentication):
    @router.get("/profile")
    async def get_profile(
        user_id: CurrentUserDep,  # Automatically extracted from JWT
        db: DatabaseDep,          # Automatically injected database
        cache: CacheDep           # Automatically injected cache
    ):
        # Check cache first
        cached = await cache.get(f"user:{user_id}")
        if cached:
            return cached
        
        # Fetch from database
        user = await db.users.find_one({"_id": user_id})
        
        # Cache for next time
        await cache.set(f"user:{user_id}", user)
        
        return user

2. Public Route (no authentication):
    @router.get("/products")
    async def list_products(
        db: DatabaseDep,
        settings: SettingsDep
    ):
        products = await db.products.find().limit(100).to_list(100)
        return {
            "products": products,
            "app_name": settings.APP_NAME
        }

3. Repository Pattern (used in modules):
    class ProductRepository:
        def __init__(self, db: DatabaseDep):
            self.db = db
            self.collection = db["products"]
        
        async def find_by_id(self, product_id: str):
            return await self.collection.find_one({"_id": product_id})

Technical Benefits:
- ✅ No global state (each request gets fresh dependencies)
- ✅ Easy to test (mock dependencies)
- ✅ Type safety (IDEs can autocomplete)
- ✅ Automatic validation and error handling
- ✅ Clean separation of concerns
"""
