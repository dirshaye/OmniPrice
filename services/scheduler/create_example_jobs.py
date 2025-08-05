"""
Example scheduled jobs for demonstration
"""

import asyncio
import logging
import sys
from datetime import datetime

# Add parent directory to Python path
sys.path.append('/home/dre/Desktop/Github/OmniPriceX')

from app.scheduler_engine import get_scheduler_engine
from app.models import JobType

logger = logging.getLogger(__name__)

async def create_example_jobs():
    """Create example scheduled jobs"""
    
    logger.info("🎯 Creating example scheduled jobs...")
    
    # Get scheduler engine
    scheduler = await get_scheduler_engine()
    
    # Job 1: Daily competitor price scraping
    daily_scrape_job = await scheduler.create_scheduled_job(
        name="Daily Competitor Price Scraping",
        job_type=JobType.SCRAPING,
        target_service="scraper-service",
        target_method="ScrapeCompetitorPrices",
        schedule_config={
            "type": "cron",
            "hour": 8,  # 8 AM UTC
            "minute": 0
        },
        parameters={
            "competitor_ids": ["amazon", "walmart", "target"],
            "product_ids": ["*"]  # All products
        },
        description="Daily scraping of competitor prices at 8 AM UTC"
    )
    
    logger.info(f"✅ Created daily scrape job: {daily_scrape_job.job_id}")
    
    # Job 2: Every 4 hours quick price check
    quick_check_job = await scheduler.create_scheduled_job(
        name="Quick Price Check",
        job_type=JobType.SCRAPING,
        target_service="scraper-service", 
        target_method="ScrapeCompetitorPrices",
        schedule_config={
            "type": "interval",
            "hours": 4
        },
        parameters={
            "competitor_ids": ["amazon"],
            "product_ids": ["top-selling-products"]  # Only top products
        },
        description="Quick price check every 4 hours for top-selling products"
    )
    
    logger.info(f"✅ Created quick check job: {quick_check_job.job_id}")
    
    # Job 3: Weekly comprehensive analysis
    weekly_analysis_job = await scheduler.create_scheduled_job(
        name="Weekly Price Analysis",
        job_type=JobType.ANALYSIS,
        target_service="scraper-service",
        target_method="ScrapeCompetitorPrices",
        schedule_config={
            "type": "cron",
            "day_of_week": "sun",  # Sunday
            "hour": 2,  # 2 AM UTC
            "minute": 0
        },
        parameters={
            "competitor_ids": ["amazon", "walmart", "target", "bestbuy"],
            "product_ids": ["*"],
            "analysis_mode": "comprehensive"
        },
        description="Comprehensive weekly price analysis on Sundays at 2 AM UTC"
    )
    
    logger.info(f"✅ Created weekly analysis job: {weekly_analysis_job.job_id}")
    
    # Job 4: Manual testing job (every 5 minutes for demo)
    test_job = await scheduler.create_scheduled_job(
        name="Test Job - Every 5 Minutes",
        job_type=JobType.SCRAPING,
        target_service="scraper-service",
        target_method="GetScraperStatus",
        schedule_config={
            "type": "interval",
            "minutes": 5
        },
        parameters={},
        description="Test job that runs every 5 minutes to check scraper status"
    )
    
    logger.info(f"✅ Created test job: {test_job.job_id}")
    
    # List all jobs
    jobs = await scheduler.list_jobs()
    logger.info(f"📋 Total scheduled jobs: {len(jobs)}")
    
    for job in jobs:
        logger.info(f"  • {job['name']} ({job['job_id']}) - Status: {job['status']}")
    
    return jobs

async def main():
    """Main function to create example jobs"""
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    try:
        jobs = await create_example_jobs()
        print(f"\n🎉 Successfully created {len(jobs)} example scheduled jobs!")
        
        print("\nJobs created:")
        for job in jobs:
            print(f"  • {job['name']}")
            print(f"    ID: {job['job_id']}")
            print(f"    Status: {job['status']}")
            print(f"    Next Run: {job['next_run_time']}")
            print()
            
    except Exception as e:
        logger.error(f"❌ Error creating example jobs: {e}")

if __name__ == "__main__":
    asyncio.run(main())
