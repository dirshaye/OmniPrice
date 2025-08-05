"""
Celery tasks for scraping operations with Playwright
"""

import asyncio
import logging
from typing import Dict, Any, List
from datetime import datetime
from celery import Celery
from .models import ScrapeJob, ScrapeJobStatus
from .config import get_settings
from .playwright_scraper import scrape_url, cleanup_scraper

settings = get_settings()
logger = logging.getLogger(__name__)

# Initialize Celery
celery_app = Celery(
    "scraper-service",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=["app.tasks"]
)

# Celery configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    result_expires=3600,
    task_routes={
        "app.tasks.scrape_product": {"queue": "scraping"},
        "app.tasks.scrape_batch": {"queue": "batch"},
    },
)

@celery_app.task(bind=True, max_retries=3)
def scrape_product(self, job_id: str, url: str, config: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Scrape a single product URL using Playwright
    """
    try:
        logger.info(f"🚀 Starting scrape job {job_id} for URL: {url}")
        
        # Update job status to running
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        async def update_job_status():
            job = await ScrapeJob.get(job_id)
            if job:
                job.status = ScrapeJobStatus.RUNNING
                job.started_at = datetime.utcnow()
                await job.save()
        
        loop.run_until_complete(update_job_status())
        
        # Scrape the URL using Playwright
        async def run_scraper():
            try:
                scraped_product = await scrape_url(url)
                return scraped_product.dict()
            except Exception as e:
                logger.error(f"❌ Playwright scraping failed: {e}")
                raise e
        
        result = loop.run_until_complete(run_scraper())
        
        # Update job with results
        async def update_job_results():
            job = await ScrapeJob.get(job_id)
            if job:
                job.status = ScrapeJobStatus.COMPLETED
                job.completed_at = datetime.utcnow()
                job.result = result
                await job.save()
        
        loop.run_until_complete(update_job_results())
        loop.close()
        
        logger.info(f"✅ Completed scrape job {job_id} - Found: {result.get('title', 'Unknown Product')}")
        return result
        
    except Exception as exc:
        logger.error(f"❌ Error in scrape job {job_id}: {exc}")
        
        # Update job status to failed
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        async def update_job_failed():
            job = await ScrapeJob.get(job_id)
            if job:
                job.status = ScrapeJobStatus.FAILED
                job.completed_at = datetime.utcnow()
                job.error_message = str(exc)
                await job.save()
        
        loop.run_until_complete(update_job_failed())
        loop.close()
        
        # Retry if we have retries left
        if self.request.retries < self.max_retries:
            retry_delay = 60 * (self.request.retries + 1)
            logger.info(f"🔄 Retrying job {job_id} in {retry_delay} seconds...")
            raise self.retry(countdown=retry_delay, exc=exc)
        
        raise exc

@celery_app.task(bind=True)
def scrape_batch(self, urls: List[str], config: Dict[str, Any] = None) -> List[Dict[str, Any]]:
    """
    Scrape multiple URLs in batch
    """
    results = []
    
    for url in urls:
        try:
            # Create a new job for each URL
            from .models import ScrapeJob
            from beanie import PydanticObjectId
            
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            async def create_and_scrape():
                job = ScrapeJob(
                    job_id=str(PydanticObjectId()),
                    url=url,
                    status=ScrapeJobStatus.PENDING
                )
                await job.create()
                
                # Run scraping task
                result = scrape_product.delay(str(job.id), url, config)
                return result.get()
            
            result = loop.run_until_complete(create_and_scrape())
            results.append(result)
            loop.close()
            
        except Exception as e:
            logger.error(f"❌ Batch scrape failed for {url}: {e}")
            results.append({"url": url, "error": str(e)})
    
    return results

# Legacy support for old task name
@celery_app.task
def run_scrape(job_id: str):
    """Legacy task - redirects to new scrape_product task"""
    
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    async def get_job_url():
        job = await ScrapeJob.get(job_id)
        return job.url if job else None
    
    url = loop.run_until_complete(get_job_url())
    loop.close()
    
    if url:
        return scrape_product.delay(job_id, url).get()
    else:
        logger.error(f"❌ Job {job_id} not found")
        return False
