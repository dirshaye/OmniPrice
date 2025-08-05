#!/usr/bin/env python3
"""
Playwright-based web scraper for e-commerce sites
Handles modern JavaScript-heavy websites with anti-detection
"""

import asyncio
import logging
from typing import Dict, Any, Optional, List
from urllib.parse import urljoin, urlparse
import json
import re
from datetime import datetime

from playwright.async_api import async_playwright, Browser, Page, TimeoutError as PlaywrightTimeoutError
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

class ScrapedProduct(BaseModel):
    """Standardized scraped product data"""
    
    # Basic info
    title: Optional[str] = None
    price: Optional[float] = None
    currency: str = "USD"
    original_price: Optional[float] = None  # Strike-through price
    availability: str = "unknown"  # in_stock, out_of_stock, limited, unknown
    
    # Additional data
    brand: Optional[str] = None
    description: Optional[str] = None
    image_urls: List[str] = Field(default_factory=list)
    rating: Optional[float] = None
    review_count: Optional[int] = None
    
    # Metadata
    source_url: str
    scraped_at: datetime = Field(default_factory=datetime.utcnow)
    raw_data: Dict[str, Any] = Field(default_factory=dict)

class PlaywrightScraper:
    """Advanced Playwright-based scraper with anti-detection"""
    
    def __init__(self):
        self.browser: Optional[Browser] = None
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        ]
        
        # Common selectors for e-commerce sites
        self.price_selectors = [
            '[data-testid*="price"]',
            '.price',
            '.product-price', 
            '.current-price',
            '.sale-price',
            '[class*="price"]',
            '[id*="price"]',
            '.a-price-whole',  # Amazon
            '.a-price-fraction',  # Amazon
            '.notranslate',  # Common price class
        ]
        
        self.title_selectors = [
            'h1',
            '.product-title',
            '[data-testid*="title"]',
            '.product-name',
            '[class*="title"]',
            '#productTitle',  # Amazon
        ]
        
        self.image_selectors = [
            '.product-image img',
            '.product-photo img', 
            '[data-testid*="image"] img',
            '.gallery img',
            '[class*="image"] img',
            '[class*="photo"] img',
        ]
    
    async def __aenter__(self):
        """Async context manager entry"""
        await self.start()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.close()
    
    async def start(self):
        """Initialize Playwright browser"""
        playwright = await async_playwright().start()
        
        # Launch browser with anti-detection settings
        self.browser = await playwright.chromium.launch(
            headless=True,
            args=[
                '--no-sandbox',
                '--disable-setuid-sandbox', 
                '--disable-dev-shm-usage',
                '--disable-accelerated-2d-canvas',
                '--no-first-run',
                '--no-zygote',
                '--single-process',
                '--disable-gpu'
            ]
        )
        
        logger.info("🚀 Playwright browser started")
    
    async def close(self):
        """Close browser"""
        if self.browser:
            await self.browser.close()
            logger.info("🛑 Playwright browser closed")
    
    async def scrape_product(self, url: str) -> ScrapedProduct:
        """Scrape product data from URL"""
        
        if not self.browser:
            await self.start()
        
        # Create new page with anti-detection
        page = await self.browser.new_page()
        
        try:
            # Set random user agent
            import random
            user_agent = random.choice(self.user_agents)
            await page.set_extra_http_headers({"User-Agent": user_agent})
            
            # Set viewport
            await page.set_viewport_size({"width": 1920, "height": 1080})
            
            # Navigate to page
            logger.info(f"🔍 Scraping: {url}")
            await page.goto(url, wait_until="domcontentloaded", timeout=30000)
            
            # Wait for page to load
            await page.wait_for_timeout(2000)
            
            # Extract product data
            product_data = await self._extract_product_data(page, url)
            
            logger.info(f"✅ Successfully scraped: {product_data.title}")
            return product_data
            
        except PlaywrightTimeoutError:
            logger.error(f"❌ Timeout scraping {url}")
            return ScrapedProduct(source_url=url, raw_data={"error": "timeout"})
            
        except Exception as e:
            logger.error(f"❌ Error scraping {url}: {e}")
            return ScrapedProduct(source_url=url, raw_data={"error": str(e)})
            
        finally:
            await page.close()
    
    async def _extract_product_data(self, page: Page, url: str) -> ScrapedProduct:
        """Extract product data from page"""
        
        # Initialize product data
        product = ScrapedProduct(source_url=url)
        
        # Extract title
        title = await self._extract_title(page)
        product.title = title
        
        # Extract price
        price_info = await self._extract_price(page)
        product.price = price_info.get("price")
        product.currency = price_info.get("currency", "USD")
        product.original_price = price_info.get("original_price")
        
        # Extract availability
        availability = await self._extract_availability(page)
        product.availability = availability
        
        # Extract images
        images = await self._extract_images(page, url)
        product.image_urls = images
        
        # Extract additional data
        additional_data = await self._extract_additional_data(page)
        product.brand = additional_data.get("brand")
        product.description = additional_data.get("description")
        product.rating = additional_data.get("rating")
        product.review_count = additional_data.get("review_count")
        
        # Store raw data for debugging
        product.raw_data = {
            "url": url,
            "scraped_at": datetime.utcnow().isoformat(),
            "user_agent": await page.evaluate("navigator.userAgent"),
            "title_raw": title,
            "price_raw": price_info,
        }
        
        return product
    
    async def _extract_title(self, page: Page) -> Optional[str]:
        """Extract product title"""
        
        for selector in self.title_selectors:
            try:
                element = await page.query_selector(selector)
                if element:
                    title = await element.inner_text()
                    if title and len(title.strip()) > 3:
                        return title.strip()
            except Exception:
                continue
        
        # Fallback to page title
        try:
            title = await page.title()
            return title.strip() if title else None
        except Exception:
            return None
    
    async def _extract_price(self, page: Page) -> Dict[str, Any]:
        """Extract price information"""
        
        price_info = {"price": None, "currency": "USD", "original_price": None}
        
        # Try different price selectors
        for selector in self.price_selectors:
            try:
                elements = await page.query_selector_all(selector)
                for element in elements:
                    text = await element.inner_text()
                    if text:
                        price = self._parse_price(text)
                        if price:
                            if not price_info["price"]:
                                price_info["price"] = price
                            else:
                                # Might be original price (higher)
                                if price > price_info["price"]:
                                    price_info["original_price"] = price
                            break
            except Exception:
                continue
        
        # Try JSON-LD structured data
        if not price_info["price"]:
            try:
                json_ld = await page.query_selector('script[type="application/ld+json"]')
                if json_ld:
                    json_text = await json_ld.inner_text()
                    data = json.loads(json_text)
                    if isinstance(data, list):
                        data = data[0]
                    
                    if "offers" in data:
                        offer = data["offers"]
                        if isinstance(offer, list):
                            offer = offer[0]
                        price_info["price"] = float(offer.get("price", 0))
                        price_info["currency"] = offer.get("priceCurrency", "USD")
            except Exception:
                pass
        
        return price_info
    
    def _parse_price(self, text: str) -> Optional[float]:
        """Parse price from text"""
        
        # Remove common currency symbols and formatting
        cleaned = re.sub(r'[^\d.,]', '', text)
        
        # Handle different decimal separators
        if ',' in cleaned and '.' in cleaned:
            # Determine which is decimal separator
            if cleaned.rfind(',') > cleaned.rfind('.'):
                # Comma is decimal separator
                cleaned = cleaned.replace('.', '').replace(',', '.')
            else:
                # Dot is decimal separator
                cleaned = cleaned.replace(',', '')
        elif ',' in cleaned:
            # Might be decimal separator in European format
            if len(cleaned.split(',')[-1]) <= 2:
                cleaned = cleaned.replace(',', '.')
            else:
                cleaned = cleaned.replace(',', '')
        
        try:
            return float(cleaned)
        except ValueError:
            return None
    
    async def _extract_availability(self, page: Page) -> str:
        """Extract availability status"""
        
        availability_indicators = {
            "in_stock": ["in stock", "available", "add to cart", "buy now", "purchase"],
            "out_of_stock": ["out of stock", "sold out", "unavailable", "not available"],
            "limited": ["limited", "few left", "hurry", "almost gone"]
        }
        
        page_text = await page.inner_text("body")
        page_text_lower = page_text.lower()
        
        for status, keywords in availability_indicators.items():
            for keyword in keywords:
                if keyword in page_text_lower:
                    return status
        
        return "unknown"
    
    async def _extract_images(self, page: Page, base_url: str) -> List[str]:
        """Extract product images"""
        
        images = []
        
        for selector in self.image_selectors:
            try:
                elements = await page.query_selector_all(selector)
                for element in elements[:5]:  # Limit to 5 images
                    src = await element.get_attribute("src")
                    if src:
                        # Convert relative URLs to absolute
                        if src.startswith("//"):
                            src = "https:" + src
                        elif src.startswith("/"):
                            src = urljoin(base_url, src)
                        
                        if src.startswith("http") and src not in images:
                            images.append(src)
            except Exception:
                continue
        
        return images
    
    async def _extract_additional_data(self, page: Page) -> Dict[str, Any]:
        """Extract additional product data"""
        
        data = {}
        
        # Try to extract brand
        brand_selectors = [
            '[class*="brand"]',
            '[data-testid*="brand"]', 
            '.manufacturer',
            '.vendor'
        ]
        
        for selector in brand_selectors:
            try:
                element = await page.query_selector(selector)
                if element:
                    brand = await element.inner_text()
                    if brand and len(brand.strip()) > 0:
                        data["brand"] = brand.strip()
                        break
            except Exception:
                continue
        
        # Try to extract description
        desc_selectors = [
            '.product-description',
            '[class*="description"]',
            '.product-details',
            '.product-info'
        ]
        
        for selector in desc_selectors:
            try:
                element = await page.query_selector(selector)
                if element:
                    desc = await element.inner_text()
                    if desc and len(desc.strip()) > 10:
                        data["description"] = desc.strip()[:500]  # Limit length
                        break
            except Exception:
                continue
        
        return data

# Singleton instance
_scraper_instance: Optional[PlaywrightScraper] = None

async def get_scraper() -> PlaywrightScraper:
    """Get or create scraper instance"""
    global _scraper_instance
    
    if _scraper_instance is None:
        _scraper_instance = PlaywrightScraper()
        await _scraper_instance.start()
    
    return _scraper_instance

async def scrape_url(url: str) -> ScrapedProduct:
    """Scrape a single URL"""
    scraper = await get_scraper()
    return await scraper.scrape_product(url)

# Cleanup function
async def cleanup_scraper():
    """Cleanup scraper resources"""
    global _scraper_instance
    
    if _scraper_instance:
        await _scraper_instance.close()
        _scraper_instance = None
