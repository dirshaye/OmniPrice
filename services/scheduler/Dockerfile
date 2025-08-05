FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY services/scheduler/requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install Flower for Celery monitoring
RUN pip install flower

# Copy shared proto files
COPY shared/ /app/shared/

# Copy application code
COPY services/scheduler/ /app/services/scheduler/

# Create logs directory
RUN mkdir -p /app/logs

# Expose gRPC port
EXPOSE 50054

# Set environment variables
ENV PYTHONPATH=/app
ENV MONGODB_URL=mongodb://mongodb:27017
ENV CELERY_BROKER_URL=amqp://guest:guest@rabbitmq:5672//
ENV CELERY_RESULT_BACKEND=redis://redis:6379/0

# Default command runs the gRPC service
# Override with docker-compose for worker/beat
CMD ["python", "services/scheduler/main.py"]
