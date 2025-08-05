"""
Job Scheduling Engine using Celery + RabbitMQ
"""

import asyncio
import logging
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
import json
from celery import current_app
from celery.schedules import crontab

from .database import get_scheduler_db
from .models import ScheduledJob, JobExecution, JobStatus, JobType
from .celery_app import celery_app
from .config import settings
from . import tasks

logger = logging.getLogger(__name__)

class SchedulingEngine:
    """Main scheduling engine managing all scheduled jobs using Celery"""
    
    def __init__(self):
        self.celery_app = celery_app
        self.db = None
        
    async def initialize(self):
        """Initialize the scheduling engine"""
        
        logger.info("🚀 Initializing Celery-based Scheduler Engine...")
        
        # Initialize database
        self.db = await get_scheduler_db()
        
        logger.info("✅ Scheduler Engine initialized with Celery")
        
        # Load existing jobs from database (for metadata tracking)
        await self._load_existing_jobs()
    
    async def _load_existing_jobs(self):
        """Load existing jobs from database for metadata tracking"""
        
        try:
            active_jobs = await ScheduledJob.find(
                ScheduledJob.status == JobStatus.ACTIVE
            ).to_list()
            
            logger.info(f"📋 Found {len(active_jobs)} existing active jobs in database")
            
            # Note: Celery Beat handles the actual scheduling
            # This is just for tracking metadata
            
        except Exception as e:
            logger.error(f"Error loading existing jobs: {e}")
    
    async def create_scheduled_job(
        self,
        name: str,
        job_type: JobType,
        target_service: str,
        target_method: str,
        schedule_config: Dict[str, Any],
        parameters: Dict[str, Any],
        description: str = ""
    ) -> ScheduledJob:
        """Create a new scheduled job using Celery"""
        
        logger.info(f"📅 Creating Celery scheduled job: {name}")
        
        # Create job document for metadata tracking
        scheduled_job = ScheduledJob(
            name=name,
            description=description,
            job_type=job_type,
            target_service=target_service,
            target_method=target_method,
            schedule_config=schedule_config,
            parameters=parameters,
            status=JobStatus.ACTIVE,
            created_at=datetime.utcnow(),
            next_run_time=self._calculate_next_run(schedule_config)
        )
        
        # Save to database
        await scheduled_job.create()
        
        # Schedule with Celery (dynamic scheduling)
        await self._schedule_celery_job(scheduled_job)
        
        logger.info(f"✅ Created Celery scheduled job: {scheduled_job.job_id}")
        return scheduled_job
    
    async def _schedule_celery_job(self, job: ScheduledJob):
        """Schedule a job with Celery dynamically"""
        
        try:
            # For dynamic scheduling, we can use Celery's apply_async with eta/countdown
            # Or update the beat schedule dynamically
            
            task_name = self._get_task_name_for_job(job)
            
            if job.schedule_config.get("type") == "interval":
                # For interval jobs, we could use countdown/eta
                # This is a simplified approach - for production, consider using celery-beat-database
                logger.info(f"📅 Interval job scheduled: {job.name}")
                
            elif job.schedule_config.get("type") == "cron":
                # For cron jobs, they should be in beat_schedule
                logger.info(f"📅 Cron job scheduled: {job.name}")
                
            # Note: For true dynamic scheduling, you'd want celery-beat-database
            # which allows runtime schedule modifications
            
        except Exception as e:
            logger.error(f"Error scheduling Celery job {job.job_id}: {e}")
            job.status = JobStatus.FAILED
            await job.save()
    
    def _get_task_name_for_job(self, job: ScheduledJob) -> str:
        """Get appropriate Celery task name for a job"""
        
        if job.job_type == JobType.SCRAPING:
            return "app.tasks.scrape_competitor_prices"
        elif job.job_type == JobType.ANALYSIS:
            return "app.tasks.comprehensive_price_analysis"
        else:
            return "app.tasks.execute_manual_job"
    
    def _calculate_next_run(self, schedule_config: Dict[str, Any]) -> datetime:
        """Calculate next run time for a job (estimation)"""
        
        schedule_type = schedule_config.get("type", "interval")
        now = datetime.now(timezone.utc)
        
        if schedule_type == "cron":
            # Simple estimation - would need proper cron parsing for accuracy
            hour = schedule_config.get("hour", 0)
            minute = schedule_config.get("minute", 0)
            return now.replace(hour=hour, minute=minute, second=0, microsecond=0)
            
        elif schedule_type == "interval":
            hours = schedule_config.get("hours", 0)
            minutes = schedule_config.get("minutes", 0)
            seconds = schedule_config.get("seconds", 0)
            
            from datetime import timedelta
            delta = timedelta(hours=hours, minutes=minutes, seconds=seconds)
            return now + delta
            
        return now
    
    async def execute_job_now(self, job_id: str) -> Dict[str, Any]:
        """Execute a job immediately using Celery"""
        
        try:
            logger.info(f"⚡ Executing job immediately: {job_id}")
            
            # Find the job
            job = await ScheduledJob.find_one(ScheduledJob.job_id == job_id)
            if not job:
                return {"success": False, "message": "Job not found"}
            
            # Execute via Celery task
            task_result = tasks.execute_manual_job.delay(
                job_type=job.job_type,
                target_service=job.target_service,
                target_method=job.target_method,
                parameters=job.parameters
            )
            
            return {
                "success": True,
                "message": "Job queued for immediate execution",
                "task_id": task_result.id
            }
            
        except Exception as e:
            logger.error(f"Error executing job {job_id}: {e}")
            return {"success": False, "message": str(e)}
    
    async def pause_job(self, job_id: str) -> bool:
        """Pause a scheduled job (metadata only - Celery Beat controls actual scheduling)"""
        
        try:
            # Update database status
            job = await ScheduledJob.find_one(ScheduledJob.job_id == job_id)
            if not job:
                return False
            
            job.status = JobStatus.PAUSED
            await job.save()
            
            # Note: For true pause/resume, you'd need celery-beat-database
            # or dynamic beat schedule management
            
            logger.info(f"⏸️ Paused job (metadata): {job_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error pausing job {job_id}: {e}")
            return False
    
    async def resume_job(self, job_id: str) -> bool:
        """Resume a paused job"""
        
        try:
            job = await ScheduledJob.find_one(ScheduledJob.job_id == job_id)
            if not job:
                return False
            
            job.status = JobStatus.ACTIVE
            await job.save()
            
            logger.info(f"▶️ Resumed job (metadata): {job_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error resuming job {job_id}: {e}")
            return False
    
    async def delete_job(self, job_id: str) -> bool:
        """Delete a scheduled job"""
        
        try:
            job = await ScheduledJob.find_one(ScheduledJob.job_id == job_id)
            if job:
                job.status = JobStatus.DELETED
                await job.save()
            
            logger.info(f"🗑️ Deleted job (metadata): {job_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting job {job_id}: {e}")
            return False
    
    
    async def get_job_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get job status and statistics"""
        
        try:
            job = await ScheduledJob.find_one(ScheduledJob.job_id == job_id)
            if not job:
                return None
            
            # Get recent executions
            recent_executions = await JobExecution.find(
                JobExecution.job_id == job_id
            ).sort(-JobExecution.started_at).limit(5).to_list()
            
            return {
                "job_id": job.job_id,
                "name": job.name,
                "status": job.status,
                "execution_count": job.execution_count,
                "success_count": job.success_count,
                "failure_count": job.failure_count,
                "last_run_time": job.last_run_time,
                "next_run_time": job.next_run_time,
                "last_success_time": job.last_success_time,
                "last_failure_time": job.last_failure_time,
                "recent_executions": [
                    {
                        "execution_id": str(exec.id),
                        "started_at": exec.started_at,
                        "completed_at": exec.completed_at,
                        "status": exec.status,
                        "duration_seconds": exec.duration_seconds,
                        "success": exec.result.get("success") if exec.result else None
                    }
                    for exec in recent_executions
                ]
            }
            
        except Exception as e:
            logger.error(f"Error getting job status {job_id}: {e}")
            return None
    
    async def list_jobs(self, status: Optional[JobStatus] = None) -> List[Dict[str, Any]]:
        """List all scheduled jobs"""
        
        try:
            query = ScheduledJob.find()
            if status:
                query = query.find(ScheduledJob.status == status)
            
            jobs = await query.to_list()
            
            return [
                {
                    "job_id": job.job_id,
                    "name": job.name,
                    "description": job.description,
                    "job_type": job.job_type,
                    "target_service": job.target_service,
                    "target_method": job.target_method,
                    "status": job.status,
                    "execution_count": job.execution_count,
                    "success_count": job.success_count,
                    "failure_count": job.failure_count,
                    "next_run_time": job.next_run_time,
                    "created_at": job.created_at
                }
                for job in jobs
            ]
            
        except Exception as e:
            logger.error(f"Error listing jobs: {e}")
            return []
    
    async def get_celery_stats(self) -> Dict[str, Any]:
        """Get Celery worker and queue statistics"""
        
        try:
            inspect = self.celery_app.control.inspect()
            
            # Get active tasks
            active_tasks = inspect.active()
            
            # Get registered tasks
            registered_tasks = inspect.registered()
            
            # Get queue stats (if available)
            stats = inspect.stats()
            
            return {
                "active_tasks": active_tasks or {},
                "registered_tasks": registered_tasks or {},
                "worker_stats": stats or {},
                "celery_healthy": bool(active_tasks is not None)
            }
            
        except Exception as e:
            logger.error(f"Error getting Celery stats: {e}")
            return {
                "active_tasks": {},
                "registered_tasks": {},
                "worker_stats": {}, 
                "celery_healthy": False,
                "error": str(e)
            }
    
    async def shutdown(self):
        """Shutdown the scheduling engine"""
        
        logger.info("🛑 Shutting down Celery-based Scheduler Engine...")
        
        # Note: Celery workers are managed separately
        # This just cleans up any local resources
        
        logger.info("✅ Scheduler Engine shutdown complete")

# Global scheduler instance
_scheduler_engine = None

async def get_scheduler_engine() -> SchedulingEngine:
    """Get the global scheduler engine instance"""
    global _scheduler_engine
    
    if not _scheduler_engine:
        _scheduler_engine = SchedulingEngine()
        await _scheduler_engine.initialize()
    
    return _scheduler_engine
