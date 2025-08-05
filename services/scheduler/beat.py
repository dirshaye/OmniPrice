#!/usr/bin/env python3
"""
Celery Beat scheduler startup script
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
            logging.FileHandler("celery_beat.log")
        ]
    )
    
    logger = logging.getLogger(__name__)
    logger.info("📅 Starting Celery Beat Scheduler...")
    
    # Start Celery Beat scheduler
    # This is equivalent to: celery -A app.celery_app beat --loglevel=info
    celery_app.start([
        'celery',
        '-A', 'app.celery_app',
        'beat',
        '--loglevel=info',
        '--schedule=/tmp/celerybeat-schedule',
        '--pidfile=/tmp/celerybeat.pid'
    ])
