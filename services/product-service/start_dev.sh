#!/bin/bash

# Product Service Development Startup Script

set -e

echo "🚀 Starting Product Service Development Environment"
echo "=================================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "${BLUE}[STEP]${NC} $1"
}

# Check if Python is installed
print_header "Checking Python installation..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    print_status "Found Python: $PYTHON_VERSION"
else
    print_error "Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

# Check if we're in the right directory
if [ ! -f "main.py" ]; then
    print_error "main.py not found. Please run this script from the product-service directory."
    exit 1
fi

# Create virtual environment if it doesn't exist
print_header "Setting up virtual environment..."
if [ ! -d "venv" ]; then
    print_status "Creating virtual environment..."
    python3 -m venv venv
else
    print_status "Virtual environment already exists"
fi

# Activate virtual environment
print_status "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
print_status "Upgrading pip..."
pip install --upgrade pip

# Install dependencies
print_header "Installing dependencies..."
if [ -f "requirements.txt" ]; then
    print_status "Installing Python packages..."
    pip install -r requirements.txt
else
    print_error "requirements.txt not found"
    exit 1
fi

# Check if .env file exists
print_header "Checking configuration..."
if [ ! -f ".env" ]; then
    print_warning ".env file not found. Using default configuration."
else
    print_status ".env file found"
fi

# Check if shared models exist
if [ ! -f "../../shared/models/product.py" ]; then
    print_warning "Shared product model not found. Some features may not work."
else
    print_status "Shared models found"
fi

# Check if proto files exist
if [ ! -f "../../shared/proto/product_service_pb2.py" ]; then
    print_warning "Proto files not found. Generating..."
    
    # Navigate to shared proto directory
    cd ../../shared/proto
    
    # Generate proto files if protoc is available
    if command -v protoc &> /dev/null; then
        print_status "Generating Python proto files..."
        python -m grpc_tools.protoc \
            --python_out=. \
            --grpc_python_out=. \
            --proto_path=. \
            product_service.proto
        print_status "Proto files generated successfully"
    else
        print_error "protoc not found. Please install protobuf compiler."
        print_error "On Ubuntu/Debian: sudo apt-get install protobuf-compiler"
        print_error "On macOS: brew install protobuf"
        exit 1
    fi
    
    # Navigate back
    cd ../../services/product-service
else
    print_status "Proto files found"
fi

# Check MongoDB connection
print_header "Checking database connection..."
print_status "Testing MongoDB connection..."

python3 -c "
import asyncio
import sys
import os
sys.path.append('.')
sys.path.append('../../shared')

async def test_db():
    try:
        from app.config import settings
        from motor.motor_asyncio import AsyncIOMotorClient
        
        client = AsyncIOMotorClient(settings.MONGO_URI)
        await client.admin.command('ping')
        print('✅ MongoDB connection successful')
        client.close()
        return True
    except Exception as e:
        print(f'❌ MongoDB connection failed: {e}')
        return False

result = asyncio.run(test_db())
sys.exit(0 if result else 1)
"

if [ $? -eq 0 ]; then
    print_status "Database connection successful"
else
    print_warning "Database connection failed. Service may not start properly."
fi

# Start the service
print_header "Starting Product Service..."
print_status "Service will start on port 50053"
print_status "Press Ctrl+C to stop the service"
print_status "Logs will be displayed below:"
echo ""

# Run the main application
python3 main.py
