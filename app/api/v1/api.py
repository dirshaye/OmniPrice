from fastapi import APIRouter
from app.api.v1.endpoints import (
    auth, products, competitors, pricing, scraper, 
    analytics, llm_assistant, admin
)

api_router = APIRouter()

# Authentication
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])

# Core entities
api_router.include_router(products.router, prefix="/products", tags=["Products"])
api_router.include_router(competitors.router, prefix="/competitors", tags=["Competitors"])
api_router.include_router(pricing.router, prefix="/pricing", tags=["Pricing"])

# Scraping
api_router.include_router(scraper.router, prefix="/scraper", tags=["Scraper"])

# Analytics & Insights
api_router.include_router(analytics.router, prefix="/analytics", tags=["Analytics"])

# LLM Assistant
api_router.include_router(llm_assistant.router, prefix="/assistant", tags=["AI Assistant"])

# Admin operations
api_router.include_router(admin.router, prefix="/admin", tags=["Admin"])
