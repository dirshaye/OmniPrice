#!/bin/bash

# OmniPriceX Deployment Script
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

echo_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

echo_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check required tools
check_requirements() {
    echo_info "Checking requirements..."
    
    if ! command -v aws &> /dev/null; then
        echo_error "AWS CLI is not installed"
        exit 1
    fi
    
    if ! command -v terraform &> /dev/null; then
        echo_error "Terraform is not installed"
        exit 1
    fi
    
    if ! command -v docker &> /dev/null; then
        echo_error "Docker is not installed"
        exit 1
    fi
    
    echo_info "All requirements satisfied"
}

# Generate gRPC code
generate_grpc() {
    echo_info "Generating gRPC code..."
    chmod +x scripts/generate_grpc.sh
    ./scripts/generate_grpc.sh
    echo_info "gRPC code generated successfully"
}

# Build and push Docker images
build_and_push_images() {
    echo_info "Building and pushing Docker images..."
    
    # Get AWS account ID and region
    AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
    AWS_REGION=${AWS_REGION:-us-east-1}
    
    # Login to ECR
    aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com
    
    # Services to build
    SERVICES=("api-gateway" "product-service" "pricing-service" "scraper-service" "competitor-service" "llm-assistant-service" "auth-service")
    
    for service in "${SERVICES[@]}"; do
        echo_info "Building $service..."
        
        # Build image
        docker build -t omnipricex-production-$service ./services/$service
        
        # Tag for ECR
        docker tag omnipricex-production-$service:latest $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/omnipricex-production-$service:latest
        docker tag omnipricex-production-$service:latest $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/omnipricex-production-$service:$(git rev-parse HEAD)
        
        # Push to ECR
        docker push $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/omnipricex-production-$service:latest
        docker push $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/omnipricex-production-$service:$(git rev-parse HEAD)
        
        echo_info "$service built and pushed successfully"
    done
}

# Deploy infrastructure
deploy_infrastructure() {
    echo_info "Deploying infrastructure with Terraform..."
    
    cd terraform
    
    # Initialize Terraform
    terraform init
    
    # Plan deployment
    terraform plan -var="image_tag=$(git rev-parse HEAD)"
    
    # Apply if user confirms
    read -p "Do you want to apply these changes? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        terraform apply -auto-approve -var="image_tag=$(git rev-parse HEAD)"
        echo_info "Infrastructure deployed successfully"
    else
        echo_warn "Deployment cancelled"
        exit 1
    fi
    
    cd ..
}

# Main deployment flow
main() {
    echo_info "Starting OmniPriceX deployment..."
    
    check_requirements
    generate_grpc
    build_and_push_images
    deploy_infrastructure
    
    echo_info "Deployment completed successfully!"
    
    # Output important information
    echo_info "Getting deployment information..."
    cd terraform
    LOAD_BALANCER_DNS=$(terraform output -raw load_balancer_dns)
    echo_info "Application URL: http://$LOAD_BALANCER_DNS"
    cd ..
}

# Parse command line arguments
case "${1:-deploy}" in
    "deploy")
        main
        ;;
    "build")
        check_requirements
        generate_grpc
        build_and_push_images
        ;;
    "infrastructure")
        check_requirements
        deploy_infrastructure
        ;;
    "grpc")
        generate_grpc
        ;;
    *)
        echo "Usage: $0 [deploy|build|infrastructure|grpc]"
        echo "  deploy        - Full deployment (default)"
        echo "  build         - Build and push Docker images only"
        echo "  infrastructure - Deploy infrastructure only"
        echo "  grpc          - Generate gRPC code only"
        exit 1
        ;;
esac
