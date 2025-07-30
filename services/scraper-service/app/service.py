import grpc
from app.proto import scraper_service_pb2
from app.proto import scraper_service_pb2_grpc
from app.database import ScrapeJob
from app.tasks import run_scrape
from beanie.exceptions import DocumentNotFound

class ScraperService(scraper_service_pb2_grpc.ScraperServiceServicer):
    async def TriggerScrape(self, request, context):
        try:
            job = ScrapeJob(
                url=request.url,
                status="PENDING",
                priority=request.priority
            )
            await job.insert()
            run_scrape.delay(job.id)
            return scraper_service_pb2.ScrapeJobStatus(id=str(job.id), status=job.status)
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return scraper_service_pb2.ScrapeJobStatus()

    async def GetScrapeJobStatus(self, request, context):
        try:
            job = await ScrapeJob.get(request.id)
            if not job:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details("Scrape job not found")
                return scraper_service_pb2.ScrapeJobStatus()
            return scraper_service_pb2.ScrapeJobStatus(id=str(job.id), status=job.status)
        except DocumentNotFound:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details("Scrape job not found")
            return scraper_service_pb2.ScrapeJobStatus()
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return scraper_service_pb2.ScrapeJobStatus()

    async def ListScrapeHistory(self, request, context):
        try:
            jobs = await ScrapeJob.find(
                ScrapeJob.status == "COMPLETED"
            ).sort(-ScrapeJob.created_at).limit(request.limit).to_list()
            
            for job in jobs:
                yield scraper_service_pb2.ScrapedData(**job.scraped_data)

        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return

