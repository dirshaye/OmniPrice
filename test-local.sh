#!/bin/bash

# OmniPriceX Local Testing Script
# This script helps test the complete application stack locally

set -e

echo "🚀 OmniPriceX Local Testing Script"
echo "=================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Docker is running
check_docker() {
    print_status "Checking Docker..."
    if ! docker info > /dev/null 2>&1; then
        print_error "Docker is not running. Please start Docker Desktop."
        exit 1
    fi
    print_success "Docker is running"
}

# Check if required files exist
check_files() {
    print_status "Checking required files..."
    
    required_files=(
        "docker-compose.yml"
        "frontend/Dockerfile"
        "frontend/package.json"
        ".env.example"
    )
    
    for file in "${required_files[@]}"; do
        if [[ ! -f "$file" ]]; then
            print_error "Required file not found: $file"
            exit 1
        fi
    done
    print_success "All required files found"
}

# Create .env file if it doesn't exist
setup_env() {
    print_status "Setting up environment variables..."
    
    if [[ ! -f ".env" ]]; then
        if [[ -f ".env.example" ]]; then
            cp .env.example .env
            print_success "Created .env from .env.example"
        else
            # Create basic .env file
            cat > .env << EOF
# Database
MONGO_URI=mongodb://mongodb:27017
MONGO_DB=omnipricex

# Authentication
JWT_SECRET=your-super-secret-jwt-key-change-this-in-production

# API Keys
GEMINI_API_KEY=your-gemini-api-key-here

# RabbitMQ
RABBITMQ_URL=amqp://guest:guest@rabbitmq:5672/

# Frontend
REACT_APP_API_URL=http://localhost:8000
EOF
            print_success "Created basic .env file"
        fi
    else
        print_success ".env file already exists"
    fi
}

# Install frontend dependencies
install_frontend_deps() {
    print_status "Installing frontend dependencies..."
    
    if [[ -d "frontend" ]]; then
        cd frontend
        if command -v npm &> /dev/null; then
            npm install
            print_success "Frontend dependencies installed"
        else
            print_warning "npm not found. Dependencies will be installed during Docker build."
        fi
        cd ..
    fi
}

# Build and start services
start_services() {
    print_status "Building and starting services..."
    
    # Stop any existing containers
    docker-compose down 2>/dev/null || true
    
    # Build and start all services
    print_status "Building Docker images... (this may take a few minutes)"
    docker-compose build
    
    print_status "Starting services..."
    docker-compose up -d
    
    print_success "Services started"
}

# Wait for services to be ready
wait_for_services() {
    print_status "Waiting for services to be ready..."
    
    # Wait for MongoDB
    print_status "Waiting for MongoDB..."
    timeout=60
    while [ $timeout -gt 0 ]; do
        if docker-compose exec -T mongodb mongosh --eval "db.runCommand('ping').ok" >/dev/null 2>&1; then
            break
        fi
        sleep 2
        timeout=$((timeout-2))
    done
    
    if [ $timeout -le 0 ]; then
        print_error "MongoDB failed to start"
        return 1
    fi
    print_success "MongoDB is ready"
    
    # Wait for API Gateway
    print_status "Waiting for API Gateway..."
    timeout=60
    while [ $timeout -gt 0 ]; do
        if curl -s http://localhost:8000/health >/dev/null 2>&1; then
            break
        fi
        sleep 2
        timeout=$((timeout-2))
    done
    
    if [ $timeout -le 0 ]; then
        print_warning "API Gateway health check failed, but continuing..."
    else
        print_success "API Gateway is ready"
    fi
    
    # Wait for Frontend
    print_status "Waiting for Frontend..."
    timeout=60
    while [ $timeout -gt 0 ]; do
        if curl -s http://localhost:3000 >/dev/null 2>&1; then
            break
        fi
        sleep 2
        timeout=$((timeout-2))
    done
    
    if [ $timeout -le 0 ]; then
        print_warning "Frontend health check failed, but continuing..."
    else
        print_success "Frontend is ready"
    fi
}

# Show service status
show_status() {
    print_status "Service Status:"
    echo ""
    docker-compose ps
    echo ""
    
    print_status "Service URLs:"
    echo -e "  ${GREEN}Frontend:${NC}     http://localhost:3000"
    echo -e "  ${GREEN}API Gateway:${NC}  http://localhost:8000"
    echo -e "  ${GREEN}MongoDB:${NC}      mongodb://localhost:27017"
    echo -e "  ${GREEN}RabbitMQ:${NC}     http://localhost:15672 (guest/guest)"
    echo ""
}

# Test basic functionality
test_services() {
    print_status "Testing basic functionality..."
    
    # Test API Gateway health
    if curl -s http://localhost:8000/health >/dev/null 2>&1; then
        print_success "API Gateway health check passed"
    else
        print_warning "API Gateway health check failed"
    fi
    
    # Test Frontend
    if curl -s http://localhost:3000 >/dev/null 2>&1; then
        print_success "Frontend is responding"
    else
        print_warning "Frontend is not responding"
    fi
    
    # Test MongoDB connection
    if docker-compose exec -T mongodb mongosh --eval "db.runCommand('ping').ok" >/dev/null 2>&1; then
        print_success "MongoDB connection successful"
    else
        print_warning "MongoDB connection failed"
    fi
}

# Show logs function
show_logs() {
    echo ""
    print_status "To view logs for specific services, use:"
    echo "  docker-compose logs frontend"
    echo "  docker-compose logs api-gateway"
    echo "  docker-compose logs mongodb"
    echo ""
    print_status "To view all logs:"
    echo "  docker-compose logs -f"
    echo ""
}

# Cleanup function
cleanup() {
    print_status "To stop all services:"
    echo "  docker-compose down"
    echo ""
    print_status "To stop and remove volumes:"
    echo "  docker-compose down -v"
    echo ""
}

# Main execution
main() {
    echo ""
    check_docker
    check_files
    setup_env
    install_frontend_deps
    start_services
    
    echo ""
    print_status "Waiting for services to initialize..."
    sleep 10
    
    wait_for_services
    show_status
    test_services
    
    echo ""
    print_success "🎉 OmniPriceX is running locally!"
    echo ""
    print_status "Open your browser and visit:"
    echo -e "  ${GREEN}http://localhost:3000${NC} - Frontend Application"
    echo -e "  ${GREEN}http://localhost:8000/docs${NC} - API Documentation"
    echo ""
    
    show_logs
    cleanup
}

# Run main function
main
