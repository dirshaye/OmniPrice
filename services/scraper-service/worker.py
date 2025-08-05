#!/usr/bin/env python3
"""
Celery worker for scraper service
"""

import os
import sys
import logging
from celery import Celery

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.tasks import celery_app
from app.config import get_settings

settings = get_settings()

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format=settings.LOG_FORMAT
)

if __name__ == "__main__":
    # Start Celery worker
    celery_app.start([
        "worker",
        "--loglevel=info",
        "--concurrency=4",
        "--queues=scraping,batch",
        "--pool=threads"  # Use threads for async operations
    ])
