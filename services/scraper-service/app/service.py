import grpc
from app.proto import scraper_service_pb2
from app.proto import scraper_service_pb2_grpc
from app.models import ScrapeJob, ScrapeJobStatus, ScrapeHistory
from app.tasks import scrape_product
from beanie.exceptions import DocumentNotFound
from beanie import PydanticObjectId
import logging

logger = logging.getLogger(__name__)

class ScraperService(scraper_service_pb2_grpc.ScraperServiceServicer):
    async def TriggerScrape(self, request, context):
        try:
            # Create scrape job
            job = ScrapeJob(
                job_id=str(PydanticObjectId()),
                url=request.url,
                status=ScrapeJobStatus.PENDING,
                priority=request.priority
            )
            await job.create()
            
            # Trigger async scraping task
            scrape_product.delay(job.job_id, request.url)
            
            logger.info(f"🚀 Triggered scrape job {job.job_id} for URL: {request.url}")
            
            return scraper_service_pb2.ScrapeJobStatus(
                id=job.job_id, 
                status=job.status.value
            )
            
        except Exception as e:
            logger.error(f"❌ Error triggering scrape: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return scraper_service_pb2.ScrapeJobStatus()

    async def GetScrapeJobStatus(self, request, context):
        try:
            # Find job by job_id
            job = await ScrapeJob.find_one(ScrapeJob.job_id == request.id)
            
            if not job:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details("Scrape job not found")
                return scraper_service_pb2.ScrapeJobStatus()
            
            # Convert result to protobuf format if available
            scraped_data = None
            if job.result:
                scraped_data = scraper_service_pb2.ScrapedData(
                    title=job.result.get("title", ""),
                    price=job.result.get("price", 0.0),
                    currency=job.result.get("currency", "USD"),
                    availability=job.result.get("availability", "unknown"),
                    source_url=job.result.get("source_url", job.url)
                )
            
            return scraper_service_pb2.ScrapeJobStatus(
                id=job.job_id,
                status=job.status.value,
                scraped_data=scraped_data,
                error_message=job.error_message or ""
            )
            
        except DocumentNotFound:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details("Scrape job not found")
            return scraper_service_pb2.ScrapeJobStatus()
        except Exception as e:
            logger.error(f"❌ Error getting job status: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return scraper_service_pb2.ScrapeJobStatus()

    async def ListScrapeHistory(self, request, context):
        try:
            # Get completed jobs
            jobs = await ScrapeJob.find(
                ScrapeJob.status == ScrapeJobStatus.COMPLETED
            ).sort(-ScrapeJob.completed_at).limit(request.limit).to_list()
            
            for job in jobs:
                if job.result:
                    scraped_data = scraper_service_pb2.ScrapedData(
                        title=job.result.get("title", ""),
                        price=job.result.get("price", 0.0),
                        currency=job.result.get("currency", "USD"),
                        availability=job.result.get("availability", "unknown"),
                        source_url=job.result.get("source_url", job.url)
                    )
                    yield scraped_data

        except Exception as e:
            logger.error(f"❌ Error listing scrape history: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return

