#!/usr/bin/env bash
set -euo pipefail

# Push OmniPrice images to AWS ECR
# Fetches repository URLs from Terraform outputs

REGION="eu-central-1"
TF_DIR="infra/terraform"

log() {
  printf '[ecr-push] %s\n' "$1"
}

# 1. Get ECR URLs from Terraform
log "Fetching ECR URLs from Terraform outputs..."
BACKEND_REPO=$(terraform -chdir=$TF_DIR output -raw ecr_repository_url_backend)
WORKER_REPO=$(terraform -chdir=$TF_DIR output -raw ecr_repository_url_worker)

# 2. Login to ECR
log "Logging in to Amazon ECR..."
aws ecr get-login-password --region $REGION | docker login --username AWS --password-stdin $BACKEND_REPO

# 3. Build & Push Backend
log "Building and pushing Backend image..."
docker build -t "$BACKEND_REPO:latest" .
docker push "$BACKEND_REPO:latest"

# 4. Build & Push Worker
log "Tagging and pushing Worker image..."
# Since worker and backend often share the same Dockerfile in this project:
docker tag "$BACKEND_REPO:latest" "$WORKER_REPO:latest"
docker push "$WORKER_REPO:latest"

log "Successfully pushed all images to ECR!"
log "Backend: $BACKEND_REPO"
log "Worker:  $WORKER_REPO"