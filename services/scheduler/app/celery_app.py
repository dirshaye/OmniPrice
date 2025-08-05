"""
Celery application configuration for Scheduler Service
"""

from celery import Celery
from celery.schedules import crontab
from .config import settings

# Create Celery app
celery_app = Celery(
    "scheduler-service",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=["app.tasks"]  # Import tasks module
)

# Configure Celery
celery_app.conf.update(
    task_serializer=settings.CELERY_TASK_SERIALIZER,
    result_serializer=settings.CELERY_RESULT_SERIALIZER,
    accept_content=settings.CELERY_ACCEPT_CONTENT,
    timezone=settings.CELERY_TIMEZONE,
    enable_utc=settings.CELERY_ENABLE_UTC,
    result_expires=3600,  # Results expire after 1 hour
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes max per task
    task_soft_time_limit=25 * 60,  # 25 minutes soft limit
    worker_prefetch_multiplier=1,  # One task at a time per worker
    worker_max_tasks_per_child=50,  # Restart worker after 50 tasks
    worker_disable_rate_limits=False,
    task_acks_late=True,  # Acknowledge task after completion
    task_reject_on_worker_lost=True,
)

# Celery Beat schedule (periodic tasks)
celery_app.conf.beat_schedule = {
    # Daily competitor price scraping at 8 AM UTC
    'daily-competitor-scraping': {
        'task': 'app.tasks.scrape_competitor_prices',
        'schedule': crontab(hour=8, minute=0),  # 8:00 AM UTC
        'args': (['amazon', 'walmart', 'target'], ['*']),  # competitor_ids, product_ids
        'options': {'queue': 'scraping'}
    },
    
    # Quick price check every 4 hours for top products
    'quick-price-check': {
        'task': 'app.tasks.scrape_competitor_prices',
        'schedule': crontab(minute=0, hour='*/4'),  # Every 4 hours
        'args': (['amazon'], ['top-selling']),
        'options': {'queue': 'scraping'}
    },
    
    # Weekly comprehensive analysis on Sundays at 2 AM
    'weekly-price-analysis': {
        'task': 'app.tasks.comprehensive_price_analysis',
        'schedule': crontab(hour=2, minute=0, day_of_week=0),  # Sunday 2 AM
        'args': (['amazon', 'walmart', 'target', 'bestbuy'],),
        'options': {'queue': 'analysis'}
    },
    
    # Health check every 5 minutes
    'health-check': {
        'task': 'app.tasks.health_check_services',
        'schedule': crontab(minute='*/5'),  # Every 5 minutes
        'options': {'queue': 'monitoring'}
    },
    
    # Clean old job execution records weekly
    'cleanup-old-records': {
        'task': 'app.tasks.cleanup_old_execution_records',
        'schedule': crontab(hour=3, minute=0, day_of_week=1),  # Monday 3 AM
        'options': {'queue': 'maintenance'}
    }
}

# Task routing - different queues for different types of work
celery_app.conf.task_routes = {
    'app.tasks.scrape_competitor_prices': {'queue': 'scraping'},
    'app.tasks.comprehensive_price_analysis': {'queue': 'analysis'},
    'app.tasks.health_check_services': {'queue': 'monitoring'},
    'app.tasks.cleanup_old_execution_records': {'queue': 'maintenance'},
    'app.tasks.execute_manual_job': {'queue': 'manual'},
}

# Default queue
celery_app.conf.task_default_queue = 'default_queue'

# Queue configuration
celery_app.conf.task_queues = {
    'scraping': {
        'exchange': 'scraping',
        'exchange_type': 'direct',
        'routing_key': 'scraping',
    },
    'analysis': {
        'exchange': 'analysis', 
        'exchange_type': 'direct',
        'routing_key': 'analysis',
    },
    'monitoring': {
        'exchange': 'monitoring',
        'exchange_type': 'direct', 
        'routing_key': 'monitoring',
    },
    'maintenance': {
        'exchange': 'maintenance',
        'exchange_type': 'direct',
        'routing_key': 'maintenance',
    },
    'manual': {
        'exchange': 'manual',
        'exchange_type': 'direct',
        'routing_key': 'manual',
    }
}
