# OmniPrice

OmniPrice is a pricing intelligence platform for retailers.

It helps teams track competitor prices, keep price history, run rule-based pricing recommendations, and use an AI assistant for pricing explanations.

## Core Features

- Product management
- Competitor URL tracking per product
- Price scraping with fallback strategy (HTTP parser + Playwright)
- URL canonicalization + dedupe per product
- Retry/DLQ worker flow for failed scrape jobs
- Price history storage
- Rule-based pricing recommendations
- Analytics endpoints (dashboard, trends, history, performance)
- LLM assistant endpoint (Gemini/OpenAI provider config)
- JWT authentication

## Tech Stack

- Backend: FastAPI
- Frontend: React + MUI
- Database: MongoDB (Atlas recommended)
- Queue: RabbitMQ
- Cache + rate limiting: Redis
- Scraping: httpx + BeautifulSoup + Playwright
- Infra: Docker, Terraform, GitHub Actions

## API Overview

Public endpoints:

- `GET /`
- `GET /health`
- `POST /api/v1/auth/register`
- `POST /api/v1/auth/login`
- `POST /api/v1/auth/login/json`
- `POST /api/v1/auth/token`

JWT-protected endpoints:

- `/api/v1/products/*`
- `/api/v1/competitors/*`
- `/api/v1/pricing/*`
- `/api/v1/analytics/*`
- `/api/v1/scraper/*`
- `/api/v1/llm/*`
- `GET /api/v1/auth/me`
- `GET /api/v1/analytics/scraper-health`

## Quick Start (Local)

1. Create env file:

```bash
cp .env.example .env
```

2. Set required values in `.env`:

- `MONGODB_URL`
- `MONGODB_DB_NAME`
- `SECRET_KEY`
- `GEMINI_API_KEY` (if testing real LLM calls)
- Optional production hardening:
  - `SCRAPER_ENFORCE_DOMAIN_ALLOWLIST=true`
  - `SCRAPER_ALLOWED_DOMAINS=migros.com.tr,a101.com.tr,sokmarket.com.tr,bim.com.tr`

3. Start services:

```bash
docker compose up --build
```

4. Open:

- Frontend: `http://localhost:3000`
- API docs: `http://localhost:8000/docs`
- Health: `http://localhost:8000/health`

## Testing

Run backend tests:

```bash
pytest -q
```

Integration tests:

```bash
pytest tests/integration -v
```

Optional E2E UI smoke tests (Playwright):

```bash
python -m playwright install chromium
pytest -m e2e tests/e2e -v
```

## Project Status

This repository is under active development. The backend core is functional and tested; frontend and cloud deployment are being actively refined.
