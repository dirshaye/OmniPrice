# OmniPriceX Makefile

.PHONY: help build up down logs clean test deploy-local deploy-aws grpc

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-15s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

# Development commands
build: ## Build all Docker images
	docker-compose build

up: ## Start all services
	docker-compose up -d

down: ## Stop all services
	docker-compose down

logs: ## Show logs from all services
	docker-compose logs -f

clean: ## Clean up containers, networks, and volumes
	docker-compose down -v --remove-orphans
	docker system prune -f

grpc: ## Generate gRPC code from proto files
	chmod +x scripts/generate_grpc.sh
	./scripts/generate_grpc.sh

# Testing
test: ## Run tests
	@echo "Running tests..."
	# Add your test commands here
	# pytest tests/ -v

# Deployment commands
deploy-local: grpc build up ## Full local deployment
	@echo "Local deployment complete!"

deploy-aws: ## Deploy to AWS using the deployment script
	chmod +x scripts/deploy.sh
	./scripts/deploy.sh

# Infrastructure commands
terraform-init: ## Initialize Terraform
	cd terraform && terraform init

terraform-plan: ## Plan Terraform changes
	cd terraform && terraform plan

terraform-apply: ## Apply Terraform changes
	cd terraform && terraform apply

terraform-destroy: ## Destroy Terraform infrastructure
	cd terraform && terraform destroy

# Docker commands
docker-login: ## Login to AWS ECR
	aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin $$(aws sts get-caller-identity --query Account --output text).dkr.ecr.us-east-1.amazonaws.com

# Development helpers
install-deps: ## Install development dependencies
	pip install -r requirements.txt
	@for service in services/*/; do \
		if [ -f "$$service/requirements.txt" ]; then \
			echo "Installing dependencies for $$service"; \
			pip install -r "$$service/requirements.txt"; \
		fi; \
	done

check-services: ## Check if all services are healthy
	@echo "Checking service health..."
	@for service in api-gateway product-service pricing-service scraper-service competitor-service llm-assistant-service auth-service; do \
		echo -n "$$service: "; \
		if docker-compose ps $$service | grep -q "Up"; then \
			echo "✅ Running"; \
		else \
			echo "❌ Not running"; \
		fi; \
	done

# Git helpers
git-hooks: ## Setup git hooks
	@echo "Setting up git hooks..."
	# Add pre-commit hooks here if needed

# Environment setup
setup-env: ## Setup environment file
	@if [ ! -f .env ]; then \
		cp .env.example .env; \
		echo "Created .env file. Please edit it with your configuration."; \
	else \
		echo ".env file already exists."; \
	fi
