# Scheduler Service - Celery + RabbitMQ Implementation

A microservice-based job scheduler using Celery, RabbitMQ, and Redis for the OmniPriceX platform.

## Architecture

```
┌─────────────────┐    ┌──────────────┐    ┌─────────────┐
│   gRPC Client   │───▶│ Scheduler    │───▶│   Celery    │
│                 │    │ Service      │    │   Worker    │
└─────────────────┘    └──────────────┘    └─────────────┘
                              │                    │
                              ▼                    ▼
                       ┌──────────────┐    ┌─────────────┐
                       │   MongoDB    │    │  RabbitMQ   │
                       │ (Job Metadata)│    │ (Message    │
                       │              │    │  Broker)    │
                       └──────────────┘    └─────────────┘
                                                  │
                                                  ▼
                                           ┌─────────────┐
                                           │    Redis    │
                                           │ (Results)   │
                                           └─────────────┘
```

## Components

### 1. **Scheduler Service (gRPC)**
- **Port**: `50054`
- **Purpose**: REST API for job management
- **Features**: Create, pause, resume, delete jobs; get status

### 2. **Celery Worker**
- **Purpose**: Execute scheduled tasks
- **Queues**: `scraping`, `analysis`, `monitoring`, `maintenance`, `manual`
- **Features**: Auto-retry, task routing, concurrency control

### 3. **Celery Beat**
- **Purpose**: Schedule periodic tasks
- **Features**: Cron-like scheduling, persistent schedules

### 4. **RabbitMQ**
- **Port**: `5672` (AMQP), `15672` (Management UI)
- **Purpose**: Message broker for task distribution
- **Features**: Task queuing, routing, reliability

### 5. **Redis**
- **Port**: `6379`
- **Purpose**: Store task results and state
- **Features**: Fast result retrieval, TTL support

### 6. **Flower**
- **Port**: `5555`
- **Purpose**: Celery monitoring web UI
- **Features**: Real-time task monitoring, worker stats

## Quick Start

### Using Docker Compose

```bash
# Start all services
docker-compose up -d

# Check service status
docker-compose ps

# View logs
docker-compose logs -f scheduler-service
docker-compose logs -f celery-worker
docker-compose logs -f celery-beat
```

### Manual Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Start RabbitMQ (if not using Docker)
brew install rabbitmq  # macOS
sudo systemctl start rabbitmq-server  # Linux

# Start Redis (if not using Docker)
brew install redis  # macOS
sudo systemctl start redis  # Linux

# Start Celery Worker
python worker.py

# Start Celery Beat (in another terminal)
python beat.py

# Start gRPC Service (in another terminal)
python main.py
```

## Scheduled Jobs

The service comes with pre-configured periodic tasks:

### 1. **Daily Competitor Scraping**
- **Schedule**: Every day at 8:00 AM UTC
- **Task**: `scrape_competitor_prices`
- **Targets**: Amazon, Walmart, Target
- **Queue**: `scraping`

### 2. **Quick Price Check**
- **Schedule**: Every 4 hours
- **Task**: `scrape_competitor_prices`
- **Targets**: Amazon (top products only)
- **Queue**: `scraping`

### 3. **Weekly Price Analysis**
- **Schedule**: Sundays at 2:00 AM UTC
- **Task**: `comprehensive_price_analysis`
- **Targets**: All major competitors
- **Queue**: `analysis`

### 4. **Health Check**
- **Schedule**: Every 5 minutes
- **Task**: `health_check_services`
- **Queue**: `monitoring`

### 5. **Cleanup**
- **Schedule**: Mondays at 3:00 AM UTC
- **Task**: `cleanup_old_execution_records`
- **Queue**: `maintenance`

## API Usage

### gRPC Methods

```python
import grpc
from shared.proto import scheduler_service_pb2_grpc, scheduler_service_pb2

# Connect to service
channel = grpc.insecure_channel('localhost:50054')
stub = scheduler_service_pb2_grpc.SchedulerServiceStub(channel)

# Create a new scheduled job
response = stub.CreateScheduledJob(
    scheduler_service_pb2.CreateScheduledJobRequest(
        name="Custom Scraping Job",
        job_type="SCRAPING",
        target_service="scraper-service",
        target_method="ScrapeCompetitorPrices",
        schedule_config=scheduler_service_pb2.ScheduleConfig(
            type="cron",
            config={"hour": "10", "minute": "0"}
        ),
        parameters={"competitor_ids": ["amazon"]},
        description="Custom job description"
    )
)

# List all jobs
jobs = stub.ListScheduledJobs(
    scheduler_service_pb2.ListScheduledJobsRequest()
)

# Execute job immediately
response = stub.ExecuteJobNow(
    scheduler_service_pb2.ExecuteJobRequest(job_id="job-123")
)

# Get job status
status = stub.GetJobStatus(
    scheduler_service_pb2.GetJobStatusRequest(job_id="job-123")
)
```

## Monitoring

### 1. **Flower Web UI**
- URL: `http://localhost:5555`
- Features: Real-time task monitoring, worker stats, task history

### 2. **RabbitMQ Management**
- URL: `http://localhost:15672`
- Login: `guest/guest`
- Features: Queue monitoring, message stats, exchanges

### 3. **Logs**
```bash
# Service logs
tail -f logs/scheduler_service.log

# Celery worker logs
tail -f logs/celery_worker.log

# Celery beat logs
tail -f logs/celery_beat.log
```

## Task Development

### Creating New Tasks

```python
# In app/tasks.py
from .celery_app import celery_app

@celery_app.task(bind=True, base=AsyncTask)
async def my_custom_task(self, param1: str, param2: int):
    """Custom task implementation"""
    
    task_id = self.request.id
    logger.info(f"🎯 Starting custom task {task_id}")
    
    try:
        # Your task logic here
        result = {"success": True, "data": "processed"}
        return result
        
    except Exception as e:
        logger.error(f"❌ Task {task_id} failed: {e}")
        raise self.retry(exc=e, countdown=60, max_retries=3)
```

### Adding to Beat Schedule

```python
# In app/celery_app.py
celery_app.conf.beat_schedule.update({
    'my-custom-schedule': {
        'task': 'app.tasks.my_custom_task',
        'schedule': crontab(hour=14, minute=30),  # 2:30 PM daily
        'args': ('param_value', 42),
        'options': {'queue': 'custom'}
    }
})
```

## Configuration

### Environment Variables

```bash
# Database
MONGODB_URL=mongodb://admin:password123@mongodb:27017

# Celery
CELERY_BROKER_URL=amqp://guest:guest@rabbitmq:5672//
CELERY_RESULT_BACKEND=redis://redis:6379/0

# Service
GRPC_PORT=50054
LOG_LEVEL=INFO

# External Services
SCRAPER_SERVICE_URL=scraper-service:50053
PRICING_SERVICE_URL=pricing-service:50052
```

### Queue Configuration

- **scraping**: Competitor price scraping tasks
- **analysis**: Data analysis and reporting tasks  
- **monitoring**: Health checks and monitoring tasks
- **maintenance**: Cleanup and maintenance tasks
- **manual**: Manually triggered tasks
- **default_queue**: Fallback queue

## Scalability

### Horizontal Scaling

```bash
# Scale workers
docker-compose up -d --scale celery-worker=4

# Or run multiple worker processes
python worker.py --concurrency=8
```

### Queue Prioritization

```python
# High priority queue
celery_app.conf.task_routes = {
    'app.tasks.urgent_task': {'queue': 'high_priority'},
    'app.tasks.normal_task': {'queue': 'normal'},
}
```

## Troubleshooting

### Common Issues

1. **Celery workers not starting**
   ```bash
   # Check RabbitMQ connection
   celery -A app.celery_app inspect ping
   
   # Check worker registration
   celery -A app.celery_app inspect registered
   ```

2. **Tasks not executing**
   ```bash
   # Check active tasks
   celery -A app.celery_app inspect active
   
   # Check queue lengths
   celery -A app.celery_app inspect queue_length
   ```

3. **Database connection issues**
   ```bash
   # Test MongoDB connection
   python -c "from app.database import get_scheduler_db; import asyncio; asyncio.run(get_scheduler_db())"
   ```

## Performance Tuning

### Worker Configuration

```python
# In celery_app.py
celery_app.conf.update(
    worker_prefetch_multiplier=1,        # Tasks per worker
    worker_max_tasks_per_child=50,       # Restart after N tasks
    task_time_limit=30 * 60,             # 30 min timeout
    task_soft_time_limit=25 * 60,        # 25 min soft limit
)
```

### Memory Management

```bash
# Monitor memory usage
docker stats celery-worker

# Restart workers periodically
celery -A app.celery_app control pool_restart
```

This Celery-based implementation provides a robust, scalable foundation for job scheduling in your microservice architecture! 🚀
