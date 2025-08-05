"""
Scheduler Service - Main gRPC Service Implementation
"""

import grpc
import asyncio
import logging
import json
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional

# Import proto files
import sys
sys.path.append('/home/dre/Desktop/Github/OmniPriceX')

from shared.proto import scheduler_service_pb2
from shared.proto import scheduler_service_pb2_grpc

from .scheduler_engine import get_scheduler_engine
from .models import JobType, JobStatus
from .database import get_scheduler_db

logger = logging.getLogger(__name__)

class SchedulerService(scheduler_service_pb2_grpc.SchedulerServiceServicer):
    """Main Scheduler Service gRPC implementation"""
    
    def __init__(self):
        self.scheduler_engine = None
        self.db = None
    
    async def initialize(self):
        """Initialize the service"""
        logger.info("🚀 Initializing Scheduler Service...")
        
        # Initialize database connection
        self.db = await get_scheduler_db()
        
        # Initialize scheduler engine
        self.scheduler_engine = await get_scheduler_engine()
        
        logger.info("✅ Scheduler Service initialized")
    
    async def CreateScheduledJob(self, request, context):
        """Create a new scheduled job"""
        
        try:
            logger.info(f"📅 Creating scheduled job: {request.name}")
            
            # Convert schedule config from proto
            schedule_config = {
                "type": request.schedule_config.type,
                **dict(request.schedule_config.config)
            }
            
            # Convert parameters from proto
            parameters = dict(request.parameters)
            
            # Create the job
            job = await self.scheduler_engine.create_scheduled_job(
                name=request.name,
                job_type=JobType(request.job_type),
                target_service=request.target_service,
                target_method=request.target_method,
                schedule_config=schedule_config,
                parameters=parameters,
                description=request.description
            )
            
            return scheduler_service_pb2.CreateScheduledJobResponse(
                success=True,
                message="Job created successfully",
                job_id=job.job_id
            )
            
        except Exception as e:
            logger.error(f"Error creating job: {e}")
            return scheduler_service_pb2.CreateScheduledJobResponse(
                success=False,
                message=f"Failed to create job: {str(e)}"
            )
    
    async def GetJobStatus(self, request, context):
        """Get job status and statistics"""
        
        try:
            status = await self.scheduler_engine.get_job_status(request.job_id)
            
            if not status:
                return scheduler_service_pb2.GetJobStatusResponse(
                    success=False,
                    message="Job not found"
                )
            
            # Build execution history
            executions = []
            for exec_data in status.get("recent_executions", []):
                executions.append(scheduler_service_pb2.JobExecution(
                    execution_id=exec_data["execution_id"],
                    started_at=exec_data["started_at"].isoformat() if exec_data["started_at"] else "",
                    completed_at=exec_data["completed_at"].isoformat() if exec_data["completed_at"] else "",
                    status=exec_data["status"],
                    duration_seconds=exec_data.get("duration_seconds", 0),
                    success=exec_data.get("success", False)
                ))
            
            return scheduler_service_pb2.GetJobStatusResponse(
                success=True,
                job_id=status["job_id"],
                name=status["name"],
                status=status["status"],
                execution_count=status["execution_count"],
                success_count=status["success_count"],
                failure_count=status["failure_count"],
                last_run_time=status["last_run_time"].isoformat() if status["last_run_time"] else "",
                next_run_time=status["next_run_time"].isoformat() if status["next_run_time"] else "",
                recent_executions=executions
            )
            
        except Exception as e:
            logger.error(f"Error getting job status: {e}")
            return scheduler_service_pb2.GetJobStatusResponse(
                success=False,
                message=f"Failed to get job status: {str(e)}"
            )
    
    async def ListScheduledJobs(self, request, context):
        """List all scheduled jobs"""
        
        try:
            # Convert status filter
            status_filter = None
            if request.status_filter:
                status_filter = JobStatus(request.status_filter)
            
            jobs = await self.scheduler_engine.list_jobs(status=status_filter)
            
            # Convert to proto format
            job_list = []
            for job in jobs:
                job_list.append(scheduler_service_pb2.ScheduledJobSummary(
                    job_id=job["job_id"],
                    name=job["name"],
                    description=job["description"],
                    job_type=job["job_type"],
                    target_service=job["target_service"],
                    target_method=job["target_method"],
                    status=job["status"],
                    execution_count=job["execution_count"],
                    success_count=job["success_count"],
                    failure_count=job["failure_count"],
                    next_run_time=job["next_run_time"].isoformat() if job["next_run_time"] else "",
                    created_at=job["created_at"].isoformat() if job["created_at"] else ""
                ))
            
            return scheduler_service_pb2.ListScheduledJobsResponse(
                success=True,
                jobs=job_list,
                total_count=len(job_list)
            )
            
        except Exception as e:
            logger.error(f"Error listing jobs: {e}")
            return scheduler_service_pb2.ListScheduledJobsResponse(
                success=False,
                message=f"Failed to list jobs: {str(e)}",
                jobs=[],
                total_count=0
            )
    
    async def PauseJob(self, request, context):
        """Pause a scheduled job"""
        
        try:
            success = await self.scheduler_engine.pause_job(request.job_id)
            
            return scheduler_service_pb2.JobControlResponse(
                success=success,
                message="Job paused successfully" if success else "Failed to pause job"
            )
            
        except Exception as e:
            logger.error(f"Error pausing job: {e}")
            return scheduler_service_pb2.JobControlResponse(
                success=False,
                message=f"Failed to pause job: {str(e)}"
            )
    
    async def ResumeJob(self, request, context):
        """Resume a paused job"""
        
        try:
            success = await self.scheduler_engine.resume_job(request.job_id)
            
            return scheduler_service_pb2.JobControlResponse(
                success=success,
                message="Job resumed successfully" if success else "Failed to resume job"
            )
            
        except Exception as e:
            logger.error(f"Error resuming job: {e}")
            return scheduler_service_pb2.JobControlResponse(
                success=False,
                message=f"Failed to resume job: {str(e)}"
            )
    
    async def DeleteJob(self, request, context):
        """Delete a scheduled job"""
        
        try:
            success = await self.scheduler_engine.delete_job(request.job_id)
            
            return scheduler_service_pb2.JobControlResponse(
                success=success,
                message="Job deleted successfully" if success else "Failed to delete job"
            )
            
        except Exception as e:
            logger.error(f"Error deleting job: {e}")
            return scheduler_service_pb2.JobControlResponse(
                success=False,
                message=f"Failed to delete job: {str(e)}"
            )
    
    async def ExecuteJobNow(self, request, context):
        """Execute a job immediately (manual trigger)"""
        
        try:
            logger.info(f"⚡ Manual execution requested for job: {request.job_id}")
            
            # Execute job immediately using Celery
            result = await self.scheduler_engine.execute_job_now(request.job_id)
            
            return scheduler_service_pb2.ExecuteJobResponse(
                success=result.get("success", False),
                message=result.get("message", "Unknown error"),
                task_id=result.get("task_id", "")
            )
            
        except Exception as e:
            logger.error(f"Error executing job: {e}")
            return scheduler_service_pb2.ExecuteJobResponse(
                success=False,
                message=f"Failed to execute job: {str(e)}"
            )
    
    async def GetSchedulerHealth(self, request, context):
        """Get scheduler service health status"""
        
        try:
            # Check scheduler engine health
            celery_stats = await self.scheduler_engine.get_celery_stats()
            
            return scheduler_service_pb2.GetSchedulerHealthResponse(
                healthy=celery_stats["celery_healthy"],
                active_jobs=len(await self.scheduler_engine.list_jobs(status=JobStatus.ACTIVE)),
                service_connections=len(celery_stats.get("worker_stats", {})),
                uptime_seconds=int(asyncio.get_event_loop().time()),
                message="Scheduler service is healthy" if celery_stats["celery_healthy"] else "Celery workers not responding"
            )
            
        except Exception as e:
            logger.error(f"Error checking health: {e}")
            return scheduler_service_pb2.GetSchedulerHealthResponse(
                healthy=False,
                active_jobs=0,
                service_connections=0,
                uptime_seconds=0,
                message=f"Health check failed: {str(e)}"
            )
    
    async def GetCeleryStats(self, request, context):
        """Get Celery worker and queue statistics (additional method)"""
        
        try:
            stats = await self.scheduler_engine.get_celery_stats()
            
            # Convert to string for protobuf
            stats_json = json.dumps(stats, indent=2, default=str)
            
            return scheduler_service_pb2.GetCeleryStatsResponse(
                success=True,
                stats_json=stats_json,
                celery_healthy=stats["celery_healthy"]
            )
            
        except Exception as e:
            logger.error(f"Error getting Celery stats: {e}")
            return scheduler_service_pb2.GetCeleryStatsResponse(
                success=False,
                stats_json=json.dumps({"error": str(e)}),
                celery_healthy=False
            )

async def serve():
    """Start the gRPC server"""
    
    logger.info("🚀 Starting Scheduler Service gRPC Server...")
    
    # Create gRPC server
    server = grpc.aio.server()
    
    # Initialize service
    scheduler_service = SchedulerService()
    await scheduler_service.initialize()
    
    # Add service to server
    scheduler_service_pb2_grpc.add_SchedulerServiceServicer_to_server(
        scheduler_service, server
    )
    
    # Configure server
    listen_addr = "0.0.0.0:50054"
    server.add_insecure_port(listen_addr)
    
    # Start server
    await server.start()
    logger.info(f"✅ Scheduler Service running on {listen_addr}")
    
    try:
        await server.wait_for_termination()
    except KeyboardInterrupt:
        logger.info("🛑 Shutting down Scheduler Service...")
        await scheduler_service.scheduler_engine.shutdown()
        await server.stop(5)

if __name__ == "__main__":
    import asyncio
    import logging
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    # Run server
    asyncio.run(serve())
