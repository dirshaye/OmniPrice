"""
Scheduler Service Database Models
"""

from beanie import Document, PydanticObjectId
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

class JobStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    RETRYING = "retrying"

class JobType(str, Enum):
    SCRAPER_JOB = "scraper_job"
    PRICING_JOB = "pricing_job"
    HEALTH_CHECK = "health_check"
    CUSTOM = "custom"

class TriggerType(str, Enum):
    CRON = "cron"
    INTERVAL = "interval"
    MANUAL = "manual"
    EVENT = "event"

class ScheduledJob(Document):
    """Scheduled job definition"""
    name: str = Field(..., description="Job name")
    description: str = Field(..., description="Job description")
    job_type: JobType = Field(..., description="Type of job")
    
    # Scheduling
    trigger_type: TriggerType = Field(..., description="How the job is triggered")
    cron_expression: Optional[str] = Field(None, description="Cron expression for cron triggers")
    interval_seconds: Optional[int] = Field(None, description="Interval in seconds for interval triggers")
    
    # Job configuration
    target_service: str = Field(..., description="Target service to call")
    target_method: str = Field(..., description="gRPC method to call")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Job parameters")
    
    # Status and control
    is_active: bool = Field(default=True, description="Whether job is active")
    max_retries: int = Field(default=3, description="Maximum retry attempts")
    retry_delay: int = Field(default=60, description="Retry delay in seconds")
    timeout_seconds: int = Field(default=300, description="Job timeout in seconds")
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: str = Field(..., description="User who created the job")
    
    # Execution stats
    last_run_at: Optional[datetime] = Field(None, description="Last execution time")
    next_run_at: Optional[datetime] = Field(None, description="Next scheduled execution")
    total_runs: int = Field(default=0, description="Total number of runs")
    success_runs: int = Field(default=0, description="Number of successful runs")
    
    class Settings:
        name = "scheduled_jobs"
        indexes = [
            "job_type",
            "is_active", 
            "next_run_at",
            "created_at",
            [("is_active", 1), ("next_run_at", 1)]
        ]

class JobExecution(Document):
    """Job execution record"""
    job_id: PydanticObjectId = Field(..., description="Reference to scheduled job")
    job_name: str = Field(..., description="Job name for quick reference")
    execution_id: str = Field(..., description="Unique execution ID")
    
    # Execution details
    status: JobStatus = Field(default=JobStatus.PENDING, description="Execution status")
    started_at: datetime = Field(default_factory=datetime.utcnow, description="Start time")
    completed_at: Optional[datetime] = Field(None, description="Completion time")
    duration_seconds: Optional[float] = Field(None, description="Execution duration")
    
    # Parameters and results
    input_parameters: Dict[str, Any] = Field(default_factory=dict, description="Input parameters")
    result_data: Dict[str, Any] = Field(default_factory=dict, description="Execution results")
    error_message: Optional[str] = Field(None, description="Error message if failed")
    error_details: Dict[str, Any] = Field(default_factory=dict, description="Detailed error info")
    
    # Retry information
    attempt_number: int = Field(default=1, description="Attempt number (1-based)")
    max_attempts: int = Field(default=3, description="Maximum attempts allowed")
    
    # Metadata
    triggered_by: str = Field(default="system", description="Who/what triggered this execution")
    node_id: Optional[str] = Field(None, description="Node that executed the job")
    
    class Settings:
        name = "job_executions"
        indexes = [
            "job_id",
            "status",
            "started_at",
            "job_name",
            [("job_id", 1), ("started_at", -1)],
            [("status", 1), ("started_at", -1)]
        ]

class JobExecutionModel(BaseModel):
    """Job execution model for API responses"""
    execution_id: str
    job_name: str
    status: JobStatus
    started_at: datetime
    completed_at: Optional[datetime] = None
    duration_seconds: Optional[float] = None
    input_parameters: Dict[str, Any] = Field(default_factory=dict)
    result_data: Dict[str, Any] = Field(default_factory=dict)
    error_message: Optional[str] = None
    attempt_number: int = 1
    triggered_by: str = "system"
