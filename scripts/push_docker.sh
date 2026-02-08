#!/usr/bin/env bash
set -euo pipefail

# Build and push OmniPrice images to a registry (Docker Hub by default)

REGISTRY="${REGISTRY:-docker.io}"
NAMESPACE="${NAMESPACE:-dirshaye}"
BACKEND_IMAGE="${BACKEND_IMAGE:-omniprice-backend}"
FRONTEND_IMAGE="${FRONTEND_IMAGE:-omniprice-frontend}"
TAG="${TAG:-latest}"

backend_ref="${REGISTRY}/${NAMESPACE}/${BACKEND_IMAGE}:${TAG}"
frontend_ref="${REGISTRY}/${NAMESPACE}/${FRONTEND_IMAGE}:${TAG}"

log() {
  printf '[images] %s\n' "$1"
}

log "building backend image -> ${backend_ref}"
docker build -t "${backend_ref}" .

log "building frontend image -> ${frontend_ref}"
docker build -t "${frontend_ref}" -f frontend/Dockerfile frontend

log "pushing backend image"
docker push "${backend_ref}"

log "pushing frontend image"
docker push "${frontend_ref}"

log "done"
log "backend:  ${backend_ref}"
log "frontend: ${frontend_ref}"
