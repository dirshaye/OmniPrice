FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY services/api-gateway/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy shared proto files
COPY shared/ /app/shared/

# Copy application code
COPY services/api-gateway/ /app/services/api-gateway/

# Set environment variables
ENV PYTHONPATH=/app

# Expose the HTTP port for API Gateway
EXPOSE 8000

# Run the application
CMD ["uvicorn", "services.api-gateway.main:app", "--host", "0.0.0.0", "--port", "8000"]
