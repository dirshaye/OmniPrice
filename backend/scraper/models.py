from django.db import models
from django.contrib.auth.models import User
import uuid

class ScrapeJob(models.Model):
    """Track scraping jobs and their status"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Job details
    job_type = models.CharField(
        max_length=20,
        choices=[
            ('single_product', 'Single Product'),
            ('competitor_bulk', 'Competitor Bulk Scrape'),
            ('category_scan', 'Category Scan'),
            ('price_check', 'Price Check'),
        ]
    )
    
    # Target information
    target_urls = models.JSONField(default=list)
    competitor_id = models.UUIDField(null=True, blank=True)
    product_ids = models.JSONField(default=list)
    
    # Status tracking
    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('running', 'Running'),
            ('completed', 'Completed'),
            ('failed', 'Failed'),
            ('cancelled', 'Cancelled'),
        ],
        default='pending'
    )
    
    # Results
    items_scraped = models.IntegerField(default=0)
    items_failed = models.IntegerField(default=0)
    error_log = models.TextField(blank=True)
    results = models.JSONField(default=dict)
    
    # Timing
    created_at = models.DateTimeField(auto_now_add=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    # Metadata
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    celery_task_id = models.CharField(max_length=255, blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.job_type} - {self.status} ({self.created_at.strftime('%Y-%m-%d %H:%M')})"
    
    @property
    def duration(self):
        """Calculate job duration"""
        if self.started_at and self.completed_at:
            return self.completed_at - self.started_at
        return None

class ScrapingError(models.Model):
    """Log scraping errors for analysis"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    scrape_job = models.ForeignKey(ScrapeJob, on_delete=models.CASCADE, related_name='errors')
    url = models.URLField()
    error_type = models.CharField(max_length=50)
    error_message = models.TextField()
    http_status = models.IntegerField(null=True, blank=True)
    
    # Context
    competitor_name = models.CharField(max_length=100, blank=True)
    product_sku = models.CharField(max_length=100, blank=True)
    
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.error_type} - {self.url[:50]}..."
