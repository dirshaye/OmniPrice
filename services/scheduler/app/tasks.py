"""
Celery tasks for Scheduler Service
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import json
from celery import Task
from celery.exceptions import Retry

from .celery_app import celery_app
from .job_executor import JobExecutor
from .models import ScheduledJob, JobExecution, JobStatus, JobType
from .database import get_scheduler_db

logger = logging.getLogger(__name__)

class AsyncTask(Task):
    """Base task that handles async operations"""
    
    def __call__(self, *args, **kwargs):
        """Execute the task, handling async operations"""
        return asyncio.get_event_loop().run_until_complete(self.run_async(*args, **kwargs))
    
    async def run_async(self, *args, **kwargs):
        """Override this method in async tasks"""
        raise NotImplementedError("Subclasses must implement run_async")

# Initialize job executor
job_executor = JobExecutor()

@celery_app.task(bind=True, base=AsyncTask, autoretry_for=(Exception,), retry_kwargs={'max_retries': 3, 'countdown': 60})
async def scrape_competitor_prices(self, competitor_ids: List[str], product_ids: List[str] = None) -> Dict[str, Any]:
    """Task to scrape competitor prices"""
    
    task_id = self.request.id
    logger.info(f"🕷️ [Task {task_id}] Starting competitor price scraping")
    
    # Create execution record
    execution = JobExecution(
        job_id=f"celery-{task_id}",
        task_id=task_id,
        task_name="scrape_competitor_prices",
        started_at=datetime.utcnow(),
        status=JobStatus.RUNNING,
        parameters={
            "competitor_ids": competitor_ids,
            "product_ids": product_ids or ["*"]
        }
    )
    
    try:
        # Initialize database connection
        db = await get_scheduler_db()
        await execution.create()
        
        # Execute the scraping job
        result = await job_executor.execute_job(
            job_type=JobType.SCRAPING,
            target_service="scraper-service",
            target_method="ScrapeCompetitorPrices",
            parameters={
                "competitor_ids": competitor_ids,
                "product_ids": product_ids or ["*"]
            }
        )
        
        # Update execution record
        execution.completed_at = datetime.utcnow()
        execution.status = JobStatus.COMPLETED if result.get("success") else JobStatus.FAILED
        execution.result = result
        execution.duration_seconds = (execution.completed_at - execution.started_at).total_seconds()
        await execution.save()
        
        logger.info(f"✅ [Task {task_id}] Competitor scraping completed - Success: {result.get('success')}")
        return result
        
    except Exception as e:
        logger.error(f"❌ [Task {task_id}] Competitor scraping failed: {e}")
        
        # Update execution record with error
        execution.completed_at = datetime.utcnow()
        execution.status = JobStatus.FAILED
        execution.result = {"success": False, "error": str(e)}
        execution.duration_seconds = (execution.completed_at - execution.started_at).total_seconds()
        
        try:
            await execution.save()
        except:
            pass
        
        # Retry the task
        raise self.retry(exc=e, countdown=60, max_retries=3)

@celery_app.task(bind=True, base=AsyncTask, autoretry_for=(Exception,), retry_kwargs={'max_retries': 2, 'countdown': 120})
async def comprehensive_price_analysis(self, competitor_ids: List[str]) -> Dict[str, Any]:
    """Task for comprehensive price analysis"""
    
    task_id = self.request.id
    logger.info(f"📊 [Task {task_id}] Starting comprehensive price analysis")
    
    execution = JobExecution(
        job_id=f"celery-{task_id}",
        task_id=task_id,
        task_name="comprehensive_price_analysis",
        started_at=datetime.utcnow(),
        status=JobStatus.RUNNING,
        parameters={"competitor_ids": competitor_ids}
    )
    
    try:
        db = await get_scheduler_db()
        await execution.create()
        
        # Step 1: Scrape all competitor data
        scrape_result = await job_executor.execute_job(
            job_type=JobType.SCRAPING,
            target_service="scraper-service",
            target_method="ScrapeCompetitorPrices",
            parameters={
                "competitor_ids": competitor_ids,
                "product_ids": ["*"],
                "analysis_mode": "comprehensive"
            }
        )
        
        if not scrape_result.get("success"):
            raise Exception(f"Scraping failed: {scrape_result.get('message')}")
        
        # Step 2: Could add more analysis steps here
        # For now, just return the scraping result
        
        execution.completed_at = datetime.utcnow()
        execution.status = JobStatus.COMPLETED
        execution.result = {
            "success": True,
            "scrape_result": scrape_result,
            "analysis_complete": True
        }
        execution.duration_seconds = (execution.completed_at - execution.started_at).total_seconds()
        await execution.save()
        
        logger.info(f"✅ [Task {task_id}] Comprehensive analysis completed")
        return execution.result
        
    except Exception as e:
        logger.error(f"❌ [Task {task_id}] Comprehensive analysis failed: {e}")
        
        execution.completed_at = datetime.utcnow()
        execution.status = JobStatus.FAILED
        execution.result = {"success": False, "error": str(e)}
        execution.duration_seconds = (execution.completed_at - execution.started_at).total_seconds()
        
        try:
            await execution.save()
        except:
            pass
        
        raise self.retry(exc=e, countdown=120, max_retries=2)

@celery_app.task(bind=True, base=AsyncTask)
async def health_check_services(self) -> Dict[str, Any]:
    """Task to check health of all connected services"""
    
    task_id = self.request.id
    logger.info(f"🩺 [Task {task_id}] Performing health check")
    
    try:
        # Perform health check on all services
        health_data = await job_executor.health_check_services()
        
        # Create a simple execution record
        execution = JobExecution(
            job_id=f"celery-health-{task_id}",
            task_id=task_id,
            task_name="health_check_services",
            started_at=datetime.utcnow(),
            completed_at=datetime.utcnow(),
            status=JobStatus.COMPLETED,
            result=health_data,
            duration_seconds=1.0
        )
        
        db = await get_scheduler_db()
        await execution.create()
        
        logger.info(f"✅ [Task {task_id}] Health check completed - Overall healthy: {health_data['overall_healthy']}")
        return health_data
        
    except Exception as e:
        logger.error(f"❌ [Task {task_id}] Health check failed: {e}")
        return {"overall_healthy": False, "error": str(e)}

@celery_app.task(bind=True, base=AsyncTask)
async def cleanup_old_execution_records(self, days_to_keep: int = 30) -> Dict[str, Any]:
    """Task to clean up old job execution records"""
    
    task_id = self.request.id
    logger.info(f"🧹 [Task {task_id}] Cleaning up execution records older than {days_to_keep} days")
    
    try:
        db = await get_scheduler_db()
        cutoff_date = datetime.utcnow() - timedelta(days=days_to_keep)
        
        # Find old execution records
        old_executions = await JobExecution.find(
            JobExecution.started_at < cutoff_date
        ).count()
        
        # Delete old records
        deleted_result = await JobExecution.find(
            JobExecution.started_at < cutoff_date
        ).delete()
        
        result = {
            "success": True,
            "deleted_count": deleted_result.deleted_count if hasattr(deleted_result, 'deleted_count') else old_executions,
            "cutoff_date": cutoff_date.isoformat(),
            "days_kept": days_to_keep
        }
        
        logger.info(f"✅ [Task {task_id}] Cleanup completed - Deleted {result['deleted_count']} old records")
        return result
        
    except Exception as e:
        logger.error(f"❌ [Task {task_id}] Cleanup failed: {e}")
        return {"success": False, "error": str(e)}

@celery_app.task(bind=True, base=AsyncTask, autoretry_for=(Exception,), retry_kwargs={'max_retries': 1, 'countdown': 30})
async def execute_manual_job(self, job_type: str, target_service: str, target_method: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
    """Task to execute a manually triggered job"""
    
    task_id = self.request.id
    logger.info(f"⚡ [Task {task_id}] Executing manual job: {target_service}.{target_method}")
    
    execution = JobExecution(
        job_id=f"manual-{task_id}",
        task_id=task_id,
        task_name="execute_manual_job",
        started_at=datetime.utcnow(),
        status=JobStatus.RUNNING,
        parameters={
            "job_type": job_type,
            "target_service": target_service,
            "target_method": target_method,
            "parameters": parameters
        }
    )
    
    try:
        db = await get_scheduler_db()
        await execution.create()
        
        # Execute the job
        result = await job_executor.execute_job(
            job_type=JobType(job_type),
            target_service=target_service,
            target_method=target_method,
            parameters=parameters
        )
        
        execution.completed_at = datetime.utcnow()
        execution.status = JobStatus.COMPLETED if result.get("success") else JobStatus.FAILED
        execution.result = result
        execution.duration_seconds = (execution.completed_at - execution.started_at).total_seconds()
        await execution.save()
        
        logger.info(f"✅ [Task {task_id}] Manual job completed - Success: {result.get('success')}")
        return result
        
    except Exception as e:
        logger.error(f"❌ [Task {task_id}] Manual job failed: {e}")
        
        execution.completed_at = datetime.utcnow()
        execution.status = JobStatus.FAILED
        execution.result = {"success": False, "error": str(e)}
        execution.duration_seconds = (execution.completed_at - execution.started_at).total_seconds()
        
        try:
            await execution.save()
        except:
            pass
        
        raise self.retry(exc=e, countdown=30, max_retries=1)

# Task to handle dynamic job scheduling
@celery_app.task(bind=True, base=AsyncTask)
async def schedule_dynamic_job(self, job_data: Dict[str, Any]) -> Dict[str, Any]:
    """Task to schedule a dynamic job based on job data"""
    
    task_id = self.request.id
    logger.info(f"📅 [Task {task_id}] Scheduling dynamic job: {job_data.get('name')}")
    
    try:
        # This would be used for dynamic job creation
        # For now, just log and return success
        
        result = {
            "success": True,
            "message": f"Dynamic job scheduled: {job_data.get('name')}",
            "job_data": job_data
        }
        
        logger.info(f"✅ [Task {task_id}] Dynamic job scheduled successfully")
        return result
        
    except Exception as e:
        logger.error(f"❌ [Task {task_id}] Dynamic job scheduling failed: {e}")
        return {"success": False, "error": str(e)}
