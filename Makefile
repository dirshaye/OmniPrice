# OmniPrice Makefile

.PHONY: help setup-env install install-frontend install-backend test test-integration test-e2e e2e-install-browser verify build up down logs clean terraform-init terraform-plan terraform-apply

help: ## Show available commands
	@echo 'Usage: make <target>'
	@echo ''
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z0-9_-]+:.*?## / {printf "  %-22s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

setup-env: ## Create .env from template if missing
	@if [ ! -f .env ]; then cp .env.example .env && echo ".env created"; else echo ".env already exists"; fi

install-backend: ## Install Python dependencies
	pip install -r requirements.txt

install-frontend: ## Install frontend dependencies
	cd frontend && npm install

install: install-backend install-frontend ## Install all dependencies

test: ## Run all backend tests (unit + integration)
	pytest -q

test-integration: ## Run integration test suite only
	pytest tests/integration -v

e2e-install-browser: ## Install Playwright Chromium browser
	python -m playwright install chromium

test-e2e: ## Run Playwright E2E tests (requires frontend+backend running)
	pytest -m e2e tests/e2e -v

verify: ## Run backend smoke verification script
	python scripts/verify_setup.py

build: ## Build Docker images
	docker compose build

up: ## Start local stack (backend, frontend, queue/cache)
	docker compose up -d --build

down: ## Stop local stack
	docker compose down

logs: ## Tail backend logs
	docker compose logs -f backend

clean: ## Remove containers, volumes, and dangling images
	docker compose down -v --remove-orphans
	docker system prune -f

terraform-init: ## Terraform init (infra/terraform)
	./scripts/deploy.sh init

terraform-plan: ## Terraform validate + plan (infra/terraform)
	./scripts/deploy.sh plan

terraform-apply: ## Terraform apply (infra/terraform)
	./scripts/deploy.sh apply
