#!/usr/bin/env python3
"""
Test script for Playwright scraper functionality
"""

import asyncio
import logging
from app.playwright_scraper import PlaywrightScraper

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_scraper():
    """Test the Playwright scraper with various e-commerce sites"""
    
    test_urls = [
        # Simple test sites
        "https://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html",
        "https://quotes.toscrape.com/",
        
        # Real e-commerce (be careful with rate limiting)
        # "https://www.example-store.com/product-page"
    ]
    
    async with PlaywrightScraper() as scraper:
        for url in test_urls:
            try:
                logger.info(f"🔍 Testing scrape of: {url}")
                
                product = await scraper.scrape_product(url)
                
                logger.info("✅ Scrape Results:")
                logger.info(f"   Title: {product.title}")
                logger.info(f"   Price: {product.price} {product.currency}")
                logger.info(f"   Availability: {product.availability}")
                logger.info(f"   Images: {len(product.image_urls)} found")
                logger.info(f"   Brand: {product.brand}")
                logger.info("---")
                
            except Exception as e:
                logger.error(f"❌ Failed to scrape {url}: {e}")

async def test_single_url():
    """Test a single URL for debugging"""
    
    # Books to Scrape - good for testing
    url = "https://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html"
    
    async with PlaywrightScraper() as scraper:
        product = await scraper.scrape_product(url)
        
        print("🎯 Detailed Scrape Results:")
        print(f"Title: {product.title}")
        print(f"Price: {product.price} {product.currency}")
        print(f"Original Price: {product.original_price}")
        print(f"Availability: {product.availability}")
        print(f"Brand: {product.brand}")
        print(f"Description: {product.description[:100] if product.description else 'None'}...")
        print(f"Images: {product.image_urls}")
        print(f"Rating: {product.rating}")
        print(f"Review Count: {product.review_count}")
        print(f"Source URL: {product.source_url}")
        print(f"Raw Data: {product.raw_data}")

if __name__ == "__main__":
    print("🚀 Testing Playwright Scraper...")
    
    # Test single URL first
    asyncio.run(test_single_url())
    
    print("\n" + "="*50 + "\n")
    
    # Test multiple URLs
    asyncio.run(test_scraper())
