import os
from celery import Celery
from django.conf import settings

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'omnipricex.settings')

app = Celery('omnipricex')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps.
app.autodiscover_tasks()

# Celery beat schedule for periodic tasks
app.conf.beat_schedule = {
    'scheduled-competitor-scraping': {
        'task': 'scraper.tasks.scheduled_competitor_scraping',
        'schedule': 3600.0,  # Run every hour
    },
    'cleanup-old-scrape-jobs': {
        'task': 'scraper.tasks.cleanup_old_scrape_jobs',
        'schedule': 86400.0,  # Run daily
    },
    'update-business-metrics': {
        'task': 'metrics.tasks.update_business_metrics',
        'schedule': 300.0,  # Run every 5 minutes
    },
}

app.conf.timezone = 'UTC'

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
