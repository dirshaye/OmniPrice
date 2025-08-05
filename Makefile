# OmniPriceX Makefile

.PHONY: help install test lint format build deploy generate-proto clean

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-15s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

# Development commands
install: ## Install all dependencies
	@echo "Installing Python dependencies..."
	@for service in services/*/; do \
		if [ -f "$$service/requirements.txt" ]; then \
			echo "Installing dependencies for $$service"; \
			pip install -r "$$service/requirements.txt"; \
		fi; \
	done
	@echo "Installing frontend dependencies..."
	cd frontend && npm install

test: ## Run all tests
	@echo "Running Python tests..."
	@for service in services/*/; do \
		if [ -d "$$service/tests" ]; then \
			echo "Testing $$service"; \
			pytest "$$service/tests/" -v; \
		fi; \
	done
	@echo "Running integration tests..."
	pytest tests/integration/ -v
	@echo "Running frontend tests..."
	cd frontend && npm test -- --coverage --watchAll=false

lint: ## Run linting on all code
	@echo "Linting Python code..."
	flake8 services/ shared/
	mypy services/ shared/
	@echo "Linting frontend code..."
	cd frontend && npm run lint

format: ## Format all code
	@echo "Formatting Python code..."
	black services/ shared/
	isort services/ shared/
	@echo "Formatting frontend code..."
	cd frontend && npm run format

build: ## Build all Docker images
	docker-compose build

deploy: ## Deploy to production
	./scripts/deploy.sh

generate-proto: ## Generate gRPC code from proto files
	chmod +x scripts/generate_grpc.sh
	./scripts/generate_grpc.sh

clean: ## Clean up containers, networks, and volumes
	docker-compose down -v --remove-orphans
	docker system prune -f

# Development workflow
dev: generate-proto build ## Setup development environment
	docker-compose up -d

# Infrastructure commands
terraform-init: ## Initialize Terraform
	cd infrastructure/terraform && terraform init

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
