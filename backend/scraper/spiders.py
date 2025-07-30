import scrapy
import json
from urllib.parse import urljoin
from decimal import Decimal
import re
import logging

logger = logging.getLogger(__name__)

class BaseProductSpider(scrapy.Spider):
    """Base spider class for product scraping"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.competitor_id = kwargs.get('competitor_id')
        self.product_urls = kwargs.get('product_urls', [])
        if isinstance(self.product_urls, str):
            self.product_urls = json.loads(self.product_urls)
    
    def start_requests(self):
        """Generate initial requests"""
        for url in self.product_urls:
            yield scrapy.Request(
                url=url,
                callback=self.parse_product,
                meta={'url': url}
            )
    
    def parse_product(self, response):
        """Override this method in specific spiders"""
        raise NotImplementedError("Subclasses must implement parse_product method")
    
    def extract_price(self, price_text):
        """Extract numeric price from text"""
        if not price_text:
            return None
        
        # Remove currency symbols and extract numbers
        price_match = re.search(r'[\d,]+\.?\d*', price_text.replace(',', ''))
        if price_match:
            try:
                return float(price_match.group().replace(',', ''))
            except ValueError:
                return None
        return None
    
    def clean_text(self, text):
        """Clean and normalize text"""
        if not text:
            return ""
        return ' '.join(text.strip().split())

class AmazonSpider(BaseProductSpider):
    """Spider for Amazon products"""
    name = 'amazon'
    allowed_domains = ['amazon.com', 'amazon.co.uk', 'amazon.de']
    
    custom_settings = {
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'DOWNLOAD_DELAY': 2,
        'RANDOMIZE_DOWNLOAD_DELAY': True,
    }
    
    def parse_product(self, response):
        """Parse Amazon product page"""
        try:
            # Extract product information
            name = response.css('#productTitle::text').get()
            name = self.clean_text(name) if name else None
            
            # Price extraction - multiple selectors for different layouts
            price_selectors = [
                '.a-price-whole::text',
                '.a-price.a-text-price.a-size-medium.apexPriceToPay .a-offscreen::text',
                '#priceblock_dealprice::text',
                '#priceblock_ourprice::text',
                '.a-price-range .a-price .a-offscreen::text'
            ]
            
            price = None
            for selector in price_selectors:
                price_text = response.css(selector).get()
                if price_text:
                    price = self.extract_price(price_text)
                    if price:
                        break
            
            # Stock status
            availability = response.css('#availability span::text').getall()
            is_in_stock = any('in stock' in text.lower() for text in availability if text)
            
            # Product details
            brand = response.css('#bylineInfo::text').get()
            brand = self.clean_text(brand) if brand else None
            
            # Rating
            rating_text = response.css('.a-icon-alt::text').get()
            rating = None
            if rating_text:
                rating_match = re.search(r'(\d+\.?\d*)', rating_text)
                if rating_match:
                    rating = float(rating_match.group())
            
            yield {
                'url': response.meta['url'],
                'competitor_id': self.competitor_id,
                'name': name,
                'price': price,
                'brand': brand,
                'rating': rating,
                'is_in_stock': is_in_stock,
                'scraped_at': response.meta.get('scraped_at'),
                'response_status': response.status,
            }
            
        except Exception as e:
            logger.error(f"Error parsing Amazon product {response.url}: {str(e)}")
            yield {
                'url': response.meta['url'],
                'error': str(e),
                'response_status': response.status,
            }

class EbaySpider(BaseProductSpider):
    """Spider for eBay products"""
    name = 'ebay'
    allowed_domains = ['ebay.com', 'ebay.co.uk', 'ebay.de']
    
    def parse_product(self, response):
        """Parse eBay product page"""
        try:
            # Extract product information
            name = response.css('#x-page-title-label::text').get()
            name = self.clean_text(name) if name else None
            
            # Price extraction
            price_selectors = [
                '.u-flL.condText span.notranslate::text',
                '.u-flL span.notranslate::text',
                '#prcIsum::text',
                '.u-flL .notranslate::text'
            ]
            
            price = None
            for selector in price_selectors:
                price_text = response.css(selector).get()
                if price_text:
                    price = self.extract_price(price_text)
                    if price:
                        break
            
            # Stock/availability
            availability = response.css('#qtySubTxt span::text').get()
            is_in_stock = availability and 'available' in availability.lower()
            
            # Seller information
            seller = response.css('.x-sellercard-atf__info__about-seller a span::text').get()
            seller = self.clean_text(seller) if seller else None
            
            yield {
                'url': response.meta['url'],
                'competitor_id': self.competitor_id,
                'name': name,
                'price': price,
                'seller': seller,
                'is_in_stock': is_in_stock,
                'scraped_at': response.meta.get('scraped_at'),
                'response_status': response.status,
            }
            
        except Exception as e:
            logger.error(f"Error parsing eBay product {response.url}: {str(e)}")
            yield {
                'url': response.meta['url'],
                'error': str(e),
                'response_status': response.status,
            }

class GenericSpider(BaseProductSpider):
    """Generic spider for other e-commerce sites"""
    name = 'generic'
    
    def parse_product(self, response):
        """Parse generic e-commerce product page"""
        try:
            # Common selectors for product information
            name_selectors = [
                'h1',
                '.product-title',
                '.product-name',
                '[data-testid="product-title"]',
                '.pdp-product-name'
            ]
            
            price_selectors = [
                '.price',
                '.product-price',
                '[data-testid="price"]',
                '.current-price',
                '.sale-price',
                '.price-current'
            ]
            
            # Extract name
            name = None
            for selector in name_selectors:
                name_elem = response.css(f'{selector}::text').get()
                if name_elem:
                    name = self.clean_text(name_elem)
                    break
            
            # Extract price
            price = None
            for selector in price_selectors:
                price_elem = response.css(f'{selector}::text').get()
                if price_elem:
                    price = self.extract_price(price_elem)
                    if price:
                        break
            
            # Basic stock check
            stock_indicators = response.css('*::text').getall()
            stock_text = ' '.join(stock_indicators).lower()
            is_in_stock = not any(phrase in stock_text for phrase in [
                'out of stock', 'sold out', 'unavailable', 'not available'
            ])
            
            yield {
                'url': response.meta['url'],
                'competitor_id': self.competitor_id,
                'name': name,
                'price': price,
                'is_in_stock': is_in_stock,
                'scraped_at': response.meta.get('scraped_at'),
                'response_status': response.status,
            }
            
        except Exception as e:
            logger.error(f"Error parsing generic product {response.url}: {str(e)}")
            yield {
                'url': response.meta['url'],
                'error': str(e),
                'response_status': response.status,
            }
