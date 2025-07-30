FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy shared proto files
COPY shared/proto /app/shared/proto

# Copy application code
COPY app/ ./app/
COPY main.py .

# Expose the gRPC port
EXPOSE 50054

# Run the application
CMD ["python", "main.py"]
