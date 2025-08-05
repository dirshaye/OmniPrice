#!/usr/bin/env python3
"""
Celery Worker startup script for Scheduler Service
"""

import os
import sys
import logging

# Add parent directory to Python path
sys.path.append('/home/dre/Desktop/Github/OmniPriceX')

from app.celery_app import celery_app

if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler("celery_worker.log")
        ]
    )
    
    logger = logging.getLogger(__name__)
    logger.info("🚀 Starting Celery Worker for Scheduler Service...")
    
    # Start Celery worker
    # This is equivalent to: celery -A app.celery_app worker --loglevel=info
    celery_app.worker_main([
        'worker',
        '--loglevel=info',
        '--concurrency=4',
        '--prefetch-multiplier=1',
        '--max-tasks-per-child=50',
        '--queues=scraping,analysis,monitoring,maintenance,manual,default_queue'
    ])
