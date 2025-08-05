"""
Scheduler Service - gRPC Clients for calling other services
"""

import grpc
import asyncio
import logging
from typing import Dict, Any, Optional
import json

# Import proto files
import sys
sys.path.append('/home/dre/Desktop/Github/OmniPriceX')

from shared.proto import scraper_service_pb2
from shared.proto import scraper_service_pb2_grpc
from .config import settings

logger = logging.getLogger(__name__)

class ServiceClient:
    """Base class for gRPC service clients"""
    
    def __init__(self, service_url: str):
        self.service_url = service_url
        self.channel = None
        
    async def connect(self):
        """Create gRPC connection"""
        if not self.channel:
            self.channel = grpc.aio.insecure_channel(self.service_url)
        return self.channel
    
    async def disconnect(self):
        """Close gRPC connection"""
        if self.channel:
            await self.channel.close()
            self.channel = None

class ScraperServiceClient(ServiceClient):
    """Client for Scraper Service"""
    
    def __init__(self):
        super().__init__(settings.SCRAPER_SERVICE_URL)
        
    async def trigger_competitor_scrape(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Trigger competitor price scraping"""
        
        try:
            channel = await self.connect()
            stub = scraper_service_pb2_grpc.ScraperServiceStub(channel)
            
            # Extract parameters
            competitor_ids = parameters.get("competitor_ids", [])
            product_ids = parameters.get("product_ids", [])
            
            logger.info(f"🕷️ Triggering scraper for competitors: {competitor_ids}")
            
            # Create request - you'll need to adjust based on actual scraper service proto
            request = scraper_service_pb2.ScrapeCompetitorPricesRequest(
                competitor_ids=competitor_ids,
                product_ids=product_ids
            )
            
            response = await stub.ScrapeCompetitorPrices(request)
            
            return {
                "success": response.success,
                "message": response.message,
                "scraped_count": response.scraped_count if hasattr(response, 'scraped_count') else 0,
                "errors": list(response.errors) if hasattr(response, 'errors') else []
            }
            
        except Exception as e:
            logger.error(f"Error calling scraper service: {e}")
            return {
                "success": False,
                "message": f"Scraper service error: {str(e)}",
                "scraped_count": 0,
                "errors": [str(e)]
            }
    
    async def get_scraper_status(self) -> Dict[str, Any]:
        """Get scraper service status"""
        
        try:
            channel = await self.connect()
            stub = scraper_service_pb2_grpc.ScraperServiceStub(channel)
            
            # Assuming there's a health check method
            request = scraper_service_pb2.GetScraperStatusRequest()
            response = await stub.GetScraperStatus(request)
            
            return {
                "healthy": True,
                "active_jobs": response.active_jobs if hasattr(response, 'active_jobs') else 0,
                "last_scrape": response.last_scrape_time if hasattr(response, 'last_scrape_time') else None
            }
            
        except Exception as e:
            logger.error(f"Error checking scraper status: {e}")
            return {
                "healthy": False,
                "error": str(e)
            }

class JobExecutor:
    """Executes scheduled jobs by calling appropriate services"""
    
    def __init__(self):
        self.scraper_client = ScraperServiceClient()
        
    async def execute_job(self, job_type: str, target_service: str, target_method: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a job by calling the appropriate service method"""
        
        logger.info(f"🎯 Executing job: {job_type} -> {target_service}.{target_method}")
        
        try:
            if target_service == "scraper-service":
                return await self._execute_scraper_job(target_method, parameters)
            else:
                return {
                    "success": False,
                    "message": f"Unknown target service: {target_service}",
                    "error": "SERVICE_NOT_FOUND"
                }
                
        except Exception as e:
            logger.error(f"Job execution error: {e}")
            return {
                "success": False,
                "message": f"Job execution failed: {str(e)}",
                "error": str(e)
            }
    
    async def _execute_scraper_job(self, method: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute scraper service job"""
        
        if method == "ScrapeCompetitorPrices":
            return await self.scraper_client.trigger_competitor_scrape(parameters)
        elif method == "GetScraperStatus":
            return await self.scraper_client.get_scraper_status()
        else:
            return {
                "success": False,
                "message": f"Unknown scraper method: {method}",
                "error": "METHOD_NOT_FOUND"
            }
    
    async def health_check_services(self) -> Dict[str, Any]:
        """Perform health check on all connected services"""
        
        results = {}
        
        # Check scraper service
        try:
            scraper_status = await self.scraper_client.get_scraper_status()
            results["scraper-service"] = scraper_status
        except Exception as e:
            results["scraper-service"] = {"healthy": False, "error": str(e)}
        
        # Overall health
        all_healthy = all(service.get("healthy", False) for service in results.values())
        
        return {
            "overall_healthy": all_healthy,
            "services": results,
            "timestamp": asyncio.get_event_loop().time()
        }
    
    async def cleanup(self):
        """Cleanup connections"""
        await self.scraper_client.disconnect()
