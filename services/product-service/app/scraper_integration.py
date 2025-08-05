#!/usr/bin/env python3
"""
Scraper Service integration for Product Service
"""

import asyncio
import logging
from typing import Optional, Dict, List
import grpc
import sys
import os

# Add shared directory to path
shared_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'shared')
shared_path = os.path.abspath(shared_path)
sys.path.insert(0, shared_path)

# Add proto directory to path  
proto_path = os.path.join(shared_path, 'proto')
sys.path.insert(0, proto_path)

import scraper_service_pb2
import scraper_service_pb2_grpc
from models.product import Product

logger = logging.getLogger(__name__)


class ScraperIntegration:
    """Integration with Scraper Service for competitor price monitoring"""
    
    def __init__(self, scraper_service_url: str = "localhost:50051"):
        self.scraper_service_url = scraper_service_url
        self.channel: Optional[grpc.aio.Channel] = None
        self.stub: Optional[scraper_service_pb2_grpc.ScraperServiceStub] = None
    
    async def connect(self):
        """Connect to Scraper Service"""
        try:
            self.channel = grpc.aio.insecure_channel(self.scraper_service_url)
            self.stub = scraper_service_pb2_grpc.ScraperServiceStub(self.channel)
            logger.info(f"✅ Connected to Scraper Service at {self.scraper_service_url}")
        except Exception as e:
            logger.error(f"❌ Failed to connect to Scraper Service: {e}")
            raise
    
    async def disconnect(self):
        """Disconnect from Scraper Service"""
        if self.channel:
            await self.channel.close()
            logger.info("🔌 Disconnected from Scraper Service")
    
    async def scrape_competitor_prices(self, product: Product) -> Dict[str, float]:
        """Scrape competitor prices for a product"""
        if not self.stub:
            await self.connect()
        
        scraped_prices = {}
        
        try:
            for competitor_name, url in product.competitor_urls.items():
                try:
                    # Create scraping request
                    scrape_request = scraper_service_pb2.ScrapeRequest(
                        url=url,
                        scraper_type="product_price",
                        selector="price",  # This would be configured per competitor
                        metadata={
                            "product_id": str(product.id),
                            "product_sku": product.sku,
                            "competitor": competitor_name
                        }
                    )
                    
                    # Perform scraping
                    response = await self.stub.ScrapeData(scrape_request)
                    
                    if response.success and response.data:
                        # Extract price from scraped data
                        price_data = response.data.get("price")
                        if price_data:
                            try:
                                price = float(price_data.replace("$", "").replace(",", ""))
                                scraped_prices[competitor_name] = price
                                
                                # Update product's competitor data
                                product.update_competitor_data(
                                    competitor_name=competitor_name,
                                    url=url,
                                    price=price,
                                    is_available=True
                                )
                                
                                logger.info(f"✅ Scraped price for {competitor_name}: ${price}")
                                
                            except (ValueError, AttributeError) as e:
                                logger.warning(f"⚠️ Invalid price format from {competitor_name}: {price_data}")
                                product.update_competitor_data(
                                    competitor_name=competitor_name,
                                    url=url,
                                    is_available=False,
                                    error=f"Invalid price format: {price_data}"
                                )
                        else:
                            logger.warning(f"⚠️ No price data found for {competitor_name}")
                            product.update_competitor_data(
                                competitor_name=competitor_name,
                                url=url,
                                is_available=False,
                                error="No price data found"
                            )
                    else:
                        logger.warning(f"⚠️ Scraping failed for {competitor_name}: {response.message}")
                        product.update_competitor_data(
                            competitor_name=competitor_name,
                            url=url,
                            is_available=False,
                            error=response.message
                        )
                
                except grpc.aio.AioRpcError as e:
                    logger.error(f"❌ gRPC error scraping {competitor_name}: {e.details()}")
                    product.update_competitor_data(
                        competitor_name=competitor_name,
                        url=url,
                        is_available=False,
                        error=f"gRPC error: {e.details()}"
                    )
                
                except Exception as e:
                    logger.error(f"❌ Unexpected error scraping {competitor_name}: {e}")
                    product.update_competitor_data(
                        competitor_name=competitor_name,
                        url=url,
                        is_available=False,
                        error=f"Unexpected error: {str(e)}"
                    )
        
        except Exception as e:
            logger.error(f"❌ Error in scrape_competitor_prices: {e}")
        
        return scraped_prices
    
    async def schedule_price_monitoring(self, product_id: str, interval_hours: int = 24):
        """Schedule regular price monitoring for a product"""
        if not self.stub:
            await self.connect()
        
        try:
            schedule_request = scraper_service_pb2.ScheduleScrapeRequest(
                url_pattern=f"product_id:{product_id}",
                interval_seconds=interval_hours * 3600,
                scraper_type="product_price_monitor",
                metadata={"product_id": product_id}
            )
            
            response = await self.stub.ScheduleScraping(schedule_request)
            
            if response.success:
                logger.info(f"✅ Scheduled price monitoring for product {product_id}")
                return response.schedule_id
            else:
                logger.error(f"❌ Failed to schedule monitoring: {response.message}")
                return None
        
        except Exception as e:
            logger.error(f"❌ Error scheduling price monitoring: {e}")
            return None
    
    async def bulk_scrape_competitor_prices(self, products: List[Product]) -> Dict[str, Dict[str, float]]:
        """Scrape competitor prices for multiple products"""
        results = {}
        
        # Use semaphore to limit concurrent scraping
        semaphore = asyncio.Semaphore(5)  # Max 5 concurrent scrapes
        
        async def scrape_single_product(product: Product):
            async with semaphore:
                try:
                    prices = await self.scrape_competitor_prices(product)
                    results[str(product.id)] = prices
                except Exception as e:
                    logger.error(f"❌ Error scraping product {product.sku}: {e}")
                    results[str(product.id)] = {}
        
        # Execute all scraping tasks concurrently
        tasks = [scrape_single_product(product) for product in products]
        await asyncio.gather(*tasks, return_exceptions=True)
        
        logger.info(f"✅ Bulk scraping completed for {len(products)} products")
        return results
    
    async def get_scraping_status(self, schedule_id: str) -> Optional[Dict]:
        """Get status of a scheduled scraping task"""
        if not self.stub:
            await self.connect()
        
        try:
            status_request = scraper_service_pb2.GetScrapeStatusRequest(
                schedule_id=schedule_id
            )
            
            response = await self.stub.GetScrapeStatus(status_request)
            
            if response.success:
                return {
                    "schedule_id": schedule_id,
                    "status": response.status,
                    "last_run": response.last_run,
                    "next_run": response.next_run,
                    "error_count": response.error_count
                }
            else:
                logger.error(f"❌ Failed to get scraping status: {response.message}")
                return None
        
        except Exception as e:
            logger.error(f"❌ Error getting scraping status: {e}")
            return None


# Global scraper integration instance
scraper_integration: Optional[ScraperIntegration] = None


async def init_scraper_integration(scraper_service_url: str = "localhost:50051"):
    """Initialize scraper integration"""
    global scraper_integration
    
    scraper_integration = ScraperIntegration(scraper_service_url)
    await scraper_integration.connect()
    return scraper_integration


async def get_scraper_integration() -> Optional[ScraperIntegration]:
    """Get scraper integration instance"""
    return scraper_integration


async def close_scraper_integration():
    """Close scraper integration"""
    if scraper_integration:
        await scraper_integration.disconnect()


# Utility functions for easy access
async def scrape_product_competitors(product: Product) -> Dict[str, float]:
    """Utility function to scrape competitor prices for a single product"""
    integration = await get_scraper_integration()
    if integration:
        return await integration.scrape_competitor_prices(product)
    return {}


async def schedule_product_monitoring(product_id: str, interval_hours: int = 24) -> Optional[str]:
    """Utility function to schedule price monitoring for a product"""
    integration = await get_scraper_integration()
    if integration:
        return await integration.schedule_price_monitoring(product_id, interval_hours)
    return None
