from fastapi import APIRouter
from omniprice.services.analytics import AnalyticsService

router = APIRouter()


@router.get("/dashboard")
async def get_dashboard():
    return await AnalyticsService.get_dashboard()


@router.get("/price-trends")
async def get_price_trends():
    return await AnalyticsService.get_price_trends(days=7)


@router.get("/competitor-distribution")
async def get_competitor_distribution():
    return await AnalyticsService.get_competitor_distribution()


@router.get("/recent-activity")
async def get_recent_activity():
    return await AnalyticsService.get_recent_activity(limit=8)


@router.get("/price-history/{product_id}")
async def get_price_history(product_id: str, days: int = 30):
    return await AnalyticsService.get_price_history(product_id, days=days)


@router.get("/market-trends")
async def get_market_trends(days: int = 14):
    return await AnalyticsService.get_market_trends(days=days)


@router.get("/performance")
async def get_performance_metrics():
    return await AnalyticsService.get_performance_metrics()


@router.get("/scraper-health")
async def get_scraper_health(hours: int = 24):
    return await AnalyticsService.get_scraper_health(hours=hours)
