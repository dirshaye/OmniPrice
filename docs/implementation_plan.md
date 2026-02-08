# OmniPrice Implementation Plan

This document tracks the practical build order for OmniPrice.

## Current Scope

- Keep architecture as a modular monolith (FastAPI + React).
- Prioritize shipping a stable product over adding extra services.
- Use Docker for local/dev parity.
- Deploy on AWS with Terraform + GitHub Actions.
- Focus market: Turkish retail price tracking (Migros, A101, Sok, Bim).

## Product Goal

Retailers can:

1. Create products.
2. Attach competitor product URLs.
3. Scrape and store competitor prices.
4. View history/analytics.
5. Get rule-based pricing recommendations.
6. Ask the LLM assistant for explanation and context.

## Productization Priorities

- Selector drift handling:
  - Keep per-site adapters and monitor extraction confidence/source.
- Retry/backoff + failure classification:
  - Use bounded retries and dead-letter queue (DLQ) instead of infinite requeue.
- Anti-bot/legal/TOS guardrails:
  - Enforce optional domain allowlist policy for production.
- Dedupe + canonical matching:
  - Canonicalize URLs and prevent duplicate competitor tracking for same product.
- Observability:
  - Track scrape success/failure, latency, domain/source metrics, and error classes.

## MVP Backlog

### Backend (high priority)

- [x] Auth (JWT)
- [x] Products API
- [x] Competitors API
- [x] Scraper fetch + enqueue API
- [x] Pricing rule API + recommendation endpoint
- [x] Analytics from real DB data
- [x] LLM endpoint with provider error handling
- [x] Integration tests for vertical slices and error paths

### Frontend (high priority)

- [x] Auth pages wired to backend
- [x] Dashboard wired to analytics endpoints
- [x] Products page CRUD wired to backend
- [x] Competitors page CRUD + manual refresh wired
- [x] Pricing page rules + recommendation wired
- [x] LLM playground wired
- [ ] Final UX polish and edge-case handling

### DevOps / Cloud (next)

- [ ] Recreate clean Terraform stack (`infra/terraform`)
- [ ] Provision AWS baseline (VPC, SG, IAM, EC2)
- [ ] Publish Docker images from GitHub Actions
- [ ] Deploy app to EC2 via compose pull/up
- [ ] Add post-deploy smoke check job

## Testing Strategy

- Unit: targeted pure logic tests.
- Integration: API-level vertical slice tests (already in place).
- E2E: Playwright smoke tests for login/register/dashboard path.

## Deployment Strategy (AWS)

Phase 1:

- EC2 + Docker Compose
- Atlas (external MongoDB)
- Redis + RabbitMQ as containers

Phase 2:

- Terraform remote state backend (S3 + DynamoDB lock)
- Harden CI/CD and rollback flow

## Non-Goals (for now)

- Full microservice split
- Lambda migration while core feature set is still changing
- Kubernetes orchestration
