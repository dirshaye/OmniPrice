from celery import shared_task
from django.utils import timezone
from django.conf import settings
import scrapy
from scrapy.crawler import CrawlerRunner
from scrapy.utils.project import get_project_settings
from twisted.internet import reactor, defer
import logging
import json
from datetime import datetime, timedelta

from core.models import Product, Competitor, CompetitorProduct, PriceHistory
from .models import ScrapeJob, ScrapingError
from .spiders import AmazonSpider, EbaySpider, GenericSpider

logger = logging.getLogger(__name__)

@shared_task(bind=True)
def scrape_competitor_prices(self, competitor_id=None, product_ids=None):
    """
    Celery task to scrape competitor prices
    """
    try:
        # Create or get scrape job
        job = ScrapeJob.objects.create(
            job_type='price_check',
            competitor_id=competitor_id,
            product_ids=product_ids or [],
            status='running',
            started_at=timezone.now(),
            celery_task_id=self.request.id
        )
        
        # Get products to scrape
        if product_ids:
            products = Product.objects.filter(id__in=product_ids, is_active=True)
        else:
            products = Product.objects.filter(is_active=True)
        
        # Get competitor
        if competitor_id:
            competitors = Competitor.objects.filter(id=competitor_id, is_active=True)
        else:
            competitors = Competitor.objects.filter(is_active=True, scraping_enabled=True)
        
        total_scraped = 0
        total_failed = 0
        
        for competitor in competitors:
            for product in products:
                try:
                    # Get competitor product mapping
                    comp_product = CompetitorProduct.objects.filter(
                        product=product,
                        competitor=competitor,
                        scraping_enabled=True
                    ).first()
                    
                    if not comp_product or not comp_product.competitor_url:
                        continue
                    
                    # Run scraping
                    result = run_spider_for_url(
                        competitor.domain,
                        comp_product.competitor_url,
                        competitor.id
                    )
                    
                    if result and 'price' in result and result['price']:
                        # Update competitor product
                        comp_product.current_competitor_price = result['price']
                        comp_product.is_in_stock = result.get('is_in_stock', True)
                        comp_product.last_checked = timezone.now()
                        comp_product.scraping_errors = 0
                        comp_product.last_error = ''
                        comp_product.save()
                        
                        # Create price history record
                        PriceHistory.objects.create(
                            product=product,
                            competitor_product=comp_product,
                            our_price=product.current_price,
                            competitor_price=result['price'],
                            price_change_reason='competitor_change'
                        )
                        
                        total_scraped += 1
                        logger.info(f"Successfully scraped {product.name} from {competitor.name}")
                        
                    else:
                        total_failed += 1
                        comp_product.scraping_errors += 1
                        comp_product.last_error = result.get('error', 'Unknown error')
                        comp_product.save()
                        
                        # Log error
                        ScrapingError.objects.create(
                            scrape_job=job,
                            url=comp_product.competitor_url,
                            error_type='scraping_failed',
                            error_message=result.get('error', 'Unknown error'),
                            competitor_name=competitor.name,
                            product_sku=product.sku
                        )
                        
                except Exception as e:
                    total_failed += 1
                    logger.error(f"Error scraping {product.name} from {competitor.name}: {str(e)}")
                    
                    # Log error
                    ScrapingError.objects.create(
                        scrape_job=job,
                        url=comp_product.competitor_url if 'comp_product' in locals() else '',
                        error_type='exception',
                        error_message=str(e),
                        competitor_name=competitor.name,
                        product_sku=product.sku
                    )
        
        # Update job status
        job.status = 'completed'
        job.completed_at = timezone.now()
        job.items_scraped = total_scraped
        job.items_failed = total_failed
        job.save()
        
        return {
            'job_id': str(job.id),
            'total_scraped': total_scraped,
            'total_failed': total_failed,
            'status': 'completed'
        }
        
    except Exception as e:
        logger.error(f"Scraping task failed: {str(e)}")
        if 'job' in locals():
            job.status = 'failed'
            job.completed_at = timezone.now()
            job.error_log = str(e)
            job.save()
        raise

def run_spider_for_url(domain, url, competitor_id):
    """
    Run appropriate spider based on domain
    """
    try:
        # Choose spider based on domain
        if 'amazon' in domain.lower():
            spider_class = AmazonSpider
        elif 'ebay' in domain.lower():
            spider_class = EbaySpider
        else:
            spider_class = GenericSpider
        
        # This is a simplified version - in production you'd use Scrapy's
        # CrawlerRunner with proper async handling
        import requests
        from bs4 import BeautifulSoup
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Simple price extraction logic (would be more sophisticated in real implementation)
        price_text = None
        price_selectors = ['.price', '.product-price', '[data-testid="price"]', '.current-price']
        
        for selector in price_selectors:
            price_elem = soup.select_one(selector)
            if price_elem:
                price_text = price_elem.get_text()
                break
        
        # Extract price number
        if price_text:
            import re
            price_match = re.search(r'[\d,]+\.?\d*', price_text.replace(',', ''))
            if price_match:
                price = float(price_match.group().replace(',', ''))
                return {
                    'price': price,
                    'is_in_stock': True,  # Simplified
                    'scraped_at': timezone.now()
                }
        
        return {'error': 'Could not extract price'}
        
    except Exception as e:
        return {'error': str(e)}

@shared_task(bind=True)
def scheduled_competitor_scraping(self):
    """
    Scheduled task to scrape all active competitors
    """
    try:
        # Get competitors that need scraping
        now = timezone.now()
        competitors_to_scrape = []
        
        for competitor in Competitor.objects.filter(is_active=True, scraping_enabled=True):
            # Check if enough time has passed since last scrape
            if not competitor.last_scraped:
                competitors_to_scrape.append(competitor)
            else:
                time_since_last = now - competitor.last_scraped
                if time_since_last.total_seconds() >= competitor.scraping_frequency:
                    competitors_to_scrape.append(competitor)
        
        results = []
        for competitor in competitors_to_scrape:
            # Start scraping task for each competitor
            task_result = scrape_competitor_prices.delay(competitor_id=str(competitor.id))
            results.append({
                'competitor': competitor.name,
                'task_id': task_result.id
            })
            
            # Update last scraped time
            competitor.last_scraped = now
            competitor.save()
        
        return {
            'scheduled_competitors': len(competitors_to_scrape),
            'tasks_started': results
        }
        
    except Exception as e:
        logger.error(f"Scheduled scraping task failed: {str(e)}")
        raise

@shared_task
def cleanup_old_scrape_jobs():
    """
    Clean up old scrape jobs and errors
    """
    try:
        # Delete scrape jobs older than 30 days
        cutoff_date = timezone.now() - timedelta(days=30)
        old_jobs = ScrapeJob.objects.filter(created_at__lt=cutoff_date)
        deleted_jobs = old_jobs.count()
        old_jobs.delete()
        
        # Delete scraping errors older than 7 days
        error_cutoff = timezone.now() - timedelta(days=7)
        old_errors = ScrapingError.objects.filter(timestamp__lt=error_cutoff)
        deleted_errors = old_errors.count()
        old_errors.delete()
        
        return {
            'deleted_jobs': deleted_jobs,
            'deleted_errors': deleted_errors
        }
        
    except Exception as e:
        logger.error(f"Cleanup task failed: {str(e)}")
        raise
